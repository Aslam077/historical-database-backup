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
                bat 'C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python312\\python.exe backup.py'
            }
        }
    }
}