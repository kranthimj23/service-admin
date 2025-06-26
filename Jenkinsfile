def image_repo = ''
def image_tag = ''

pipeline {
    agent any

    environment {
        PROJECT_ID = 'devops-ai-labs-1'
        CLUSTER = 'demo-gke-cluster'
        ZONE = 'asia-south1'
        GCP_KEY = 'C:\\Users\\himan\\Downloads\\devops-ai-labs-1-a017a42fd880.json'
        PYTHON_EXEC = 'C:\\Users\\himan\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        GIT_CREDENTIALS_ID = credentials('Jenkins-cred-new')
    }

    stages {
 
       stage('Checkout with credentials') {
            steps {
                deleteDir()
                script {
                    withCredentials([string(credentialsId: 'Jenkins-cred-new', variable: 'GIT_TOKEN')]) {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/dev"]],
                            userRemoteConfigs: [[
                                url: "https://${GIT_TOKEN}@github.com/kranthimj23/service-admin.git"
                            ]]
                        ])
                    }
                }
            }
        }

        stage('Authenticate with GCP') {
            steps {
                bat """
                    gcloud auth activate-service-account --key-file="${env.GCP_KEY}"
                    gcloud config set project ${env.PROJECT_ID}
                    gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    image_repo = "asia-south1-docker.pkg.dev/${env.PROJECT_ID}/service-admin/admin"
                    image_tag = "${BUILD_NUMBER}-${env.env_namespace}"
                    def image_full = "${image_repo}:${image_tag}"

                    bat """
                        docker build -t ${image_full} .
                        docker push ${image_full}
                    """
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                bat """
                    gcloud container clusters get-credentials ${env.CLUSTER} --region ${env.ZONE} --project ${env.PROJECT_ID}
                """

                configFileProvider([configFile(fileId: 'deploy_to_gke', targetLocation: 'deploy_to_gke.py')]) {
                     script {
                            def pythonCommand = """
                                set CLUSTER=${env.CLUSTER}
                                set ZONE=${env.ZONE}
                                set PROJECT_ID=${env.PROJECT_ID}
                                echo Running Python script...
                                ${env.PYTHON_EXEC} deploy_to_gke.py ${env.env_namespace} ${image_repo} ${image_tag} ${env.github_url}
                            """
                        
                            echo "Executing Python Deployment Script..."
                        
                            def result = bat(script: pythonCommand, returnStdout: true).trim()
                            echo "Deployment Output:\n${result}"
                        }

                }
            }
        }
    }
}
