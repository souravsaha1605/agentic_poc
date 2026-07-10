# First, create a resource group (if you haven't already)
az group create --name aiagent-course-rg --location eastus

# Deploy the Bicep file
az deployment group create --resource-group aiagent-course-rg --template-file ai_103_bicep_unit_1.bicep --parameters coursePrefix=sahaudemyagenticcourse

# Get your deployment outputs
az deployment group show --resource-group aiagent-course-rg --name ai_103_bicep_unit_1 --query properties.outputs

