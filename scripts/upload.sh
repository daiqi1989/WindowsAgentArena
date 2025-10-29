az login
# potentially needed if commands below don't work: az acr login --name <ACR_NAME>
sudo docker login waaws2cr.azurecr.io # you will be prompted to enter your ACR credentials (username + password which can be found in the Azure portal)

sudo docker tag winarena waaws2cr.azurecr.io/winarena:latest
sudo docker push waaws2cr.azurecr.io/winarena:latest