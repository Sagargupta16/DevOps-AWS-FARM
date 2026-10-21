# AWS setup for the deploy pipeline

[`deploy.yml`](../.github/workflows/deploy.yml) is written against the resources below. Nothing here is created by the repo: run the commands once in your own account, set the repo variables, then flip `DEPLOY_ENABLED` to `true`.

The pipeline holds no AWS keys. GitHub issues the job an OIDC token, and AWS exchanges it for a role that only this repo's `production` environment can assume.

| File | What it is |
| --- | --- |
| [`github-oidc-trust-policy.json`](github-oidc-trust-policy.json) | Trust policy for the deploy role. The `sub` condition pins it to `repo:Sagargupta16/farm-stack-aws-ecs:environment:production`, so another repo, a fork or a job outside the environment cannot assume it |
| [`deploy-role-policy.json`](deploy-role-policy.json) | Least-privilege permissions for the deploy role: push to one ECR repository, register task definitions, update one ECS service, pass the two task roles to ECS only |
| [`task-definition.json`](task-definition.json) | First revision of the Fargate task: 0.25 vCPU, 512 MiB, `MONGODB_URL` from Secrets Manager, JSON logs to CloudWatch, container health check on `/health` |

Replace `<ACCOUNT_ID>` and `<REGION>` in the three files before use. The names below (`devops-aws-farm` for the repository, cluster, service and log group) match the files; change them together if you rename.

## One-time setup

Run in a shell with admin credentials for the target account (bash shown; in PowerShell replace the trailing `\` with a backtick).

```bash
# 1. Let GitHub Actions federate into the account (skip if the provider already exists)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com

# 2. Deploy role assumed by the workflow
aws iam create-role --role-name devops-aws-farm-deploy \
  --assume-role-policy-document file://aws/github-oidc-trust-policy.json
aws iam put-role-policy --role-name devops-aws-farm-deploy \
  --policy-name deploy --policy-document file://aws/deploy-role-policy.json

# 3. Image registry: immutable tags (every image is tagged with its commit SHA) and scan on push
aws ecr create-repository --repository-name devops-aws-farm \
  --image-tag-mutability IMMUTABLE \
  --image-scanning-configuration scanOnPush=true

# 4. Connection string lives in Secrets Manager, never in the image or the task definition
aws secretsmanager create-secret --name devops-aws-farm/mongodb-url \
  --secret-string 'mongodb+srv://USER:PASSWORD@cluster.example.mongodb.net/blogging'

# 5. Log group the awslogs driver writes the JSON logs to
aws logs create-log-group --log-group-name /ecs/devops-aws-farm
aws logs put-retention-policy --log-group-name /ecs/devops-aws-farm --retention-in-days 14
```

Task execution role `devops-aws-farm-task-execution`: trust `ecs-tasks.amazonaws.com`, attach `AmazonECSTaskExecutionRolePolicy`, and allow `secretsmanager:GetSecretValue` on the secret from step 4. Task role `devops-aws-farm-task`: same trust, no policies (the app calls no AWS APIs).

Then register the first task definition and create the service. The ALB target group must use `/health` as its health check path: it returns 200 only when MongoDB answers a ping, so a task that cannot reach the database is taken out of rotation.

```bash
aws ecs create-cluster --cluster-name devops-aws-farm
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json

aws elbv2 create-target-group --name devops-aws-farm --protocol HTTP --port 8000 \
  --target-type ip --vpc-id <VPC_ID> --health-check-path /health

# The circuit breaker stops a rollout whose tasks keep failing and rolls back to the last good revision
aws ecs create-service --cluster devops-aws-farm --service-name devops-aws-farm \
  --task-definition devops-aws-farm --desired-count 1 --launch-type FARGATE \
  --deployment-configuration "deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200" \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_IDS>],securityGroups=[<SG_ID>],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=<TARGET_GROUP_ARN>,containerName=app,containerPort=8000"
```

The first revision points at a `bootstrap` tag that does not exist yet, so the service starts with no healthy tasks. The first pipeline run replaces it with a SHA-tagged image.

## Wire up the repo

```bash
gh variable set AWS_ROLE_ARN       --body arn:aws:iam::<ACCOUNT_ID>:role/devops-aws-farm-deploy
gh variable set AWS_REGION         --body <REGION>
gh variable set ECR_REPOSITORY     --body devops-aws-farm
gh variable set ECS_CLUSTER        --body devops-aws-farm
gh variable set ECS_SERVICE        --body devops-aws-farm
gh variable set ECS_TASK_FAMILY    --body devops-aws-farm
gh variable set ECS_CONTAINER_NAME --body app
gh variable set APP_URL            --body https://<ALB_DNS_NAME>   # optional: enables the /health smoke test
gh variable set DEPLOY_ENABLED     --body true
```

In **Settings > Environments > production**, add yourself under **Required reviewers**. Every deploy then waits for an approval before it can request AWS credentials. The environment appears after the first run that references it.

Run it from **Actions > Deploy to AWS ECS > Run workflow**.

## Tear down

```bash
aws ecs update-service --cluster devops-aws-farm --service devops-aws-farm --desired-count 0
aws ecs delete-service --cluster devops-aws-farm --service devops-aws-farm --force
aws ecs delete-cluster --cluster devops-aws-farm
aws ecr delete-repository --repository-name devops-aws-farm --force
aws secretsmanager delete-secret --secret-id devops-aws-farm/mongodb-url --force-delete-without-recovery
aws logs delete-log-group --log-group-name /ecs/devops-aws-farm
aws iam delete-role-policy --role-name devops-aws-farm-deploy --policy-name deploy
aws iam delete-role --role-name devops-aws-farm-deploy
gh variable set DEPLOY_ENABLED --body false
```

Delete the target group, load balancer and the two task roles the same way if you created them for this.
