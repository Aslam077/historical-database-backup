pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Run Backup') {
            steps {
                bat 'py backup.py'
            }
        }
    }
}