# Create the helm chart
` helm create final-pj1 `

# Install the first one
` helm install mypj-release .\final-pj1 `

# Upgrade after templating 
` helm upgrade mypj-release .\final-pj1 --values .\final-pj1\values.yaml  `

# Accessing to the application
` kubectl get pods `
` kubectl port-forward <flask-app-XXXXXXXXXX-XXXXX> 5000:5000 `

# In your browser
` http://localhost:5000 `

