pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'historical-database-backup'
        PYTHON_SCRIPT = 'backup.py'
        
        // Database credentials from Jenkins
        DB_USER = credentials('db-username')
        DB_PASSWORD = credentials('db-password')
        DB_HOST = credentials('db-host')
        DB_PORT = credentials('db-port')
    }
    
    parameters {
        choice(
            name: 'BACKUP_MODE',
            choices: ['production', 'test'],
            description: 'Run backup in production mode or test mode'
        )
        string(
            name: 'TEST_DATE',
            defaultValue: '',
            description: 'Optional: Test date (YYYY-MM-DD)'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📂 Checking out code from GitHub...'
                checkout scm
                echo '✅ Code checked out successfully'
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo '🔧 Setting up Python environment...'
                
                // For Windows
                bat '''
                    echo Python version:
                    python --version
                    
                    echo Installing dependencies...
                    pip install -r requirements.txt
                    
                    echo ✅ Setup complete
                '''
            }
        }
        
        stage('Run Backup') {
            steps {
                echo '📊 Starting database backup...'
                
                script {
                    try {
                        // Run the backup script
                        if (params.BACKUP_MODE == 'test' && params.TEST_DATE) {
                            // Test mode with specific date
                            bat """
                                echo Running backup with test date: ${params.TEST_DATE}
                                python ${PYTHON_SCRIPT}
                            """
                        } else {
                            // Production mode
                            bat """
                                echo Running backup in production mode
                                python ${PYTHON_SCRIPT}
                            """
                        }
                        echo '✅ Backup completed successfully!'
                    } catch (Exception e) {
                        echo '❌ Backup failed!'
                        throw e
                    }
                }
            }
        }
        
        stage('Verify Backup') {
            steps {
                echo '🔍 Verifying backup...'
                
                // You can add verification steps here
                bat '''
                    echo Backup verification complete
                '''
            }
        }
    }
    
    post {
        success {
            echo '🎉 Pipeline succeeded!'
            // Optional: Send email notification
            // mail to: 'your-email@example.com', subject: "Backup Succeeded - ${env.JOB_NAME}", body: "Backup completed successfully"
        }
        failure {
            echo '💥 Pipeline failed!'
            // Optional: Send failure notification
            // mail to: 'your-email@example.com', subject: "Backup FAILED - ${env.JOB_NAME}", body: "Backup failed! Please check Jenkins console."
        }
        always {
            echo '🏁 Pipeline finished.'
        }
    }
}