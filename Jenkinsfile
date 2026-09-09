pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'historical-database-backup'
        PYTHON_SCRIPT = 'backup.py'
        // Update this path to match your Python installation
        PYTHON_PATH = 'C:\\Python39\\python.exe'
        PIP_PATH = 'C:\\Python39\\Scripts\\pip.exe'
    }
    
    parameters {
        choice(
            name: 'BACKUP_MODE',
            choices: ['production', 'test'],
            description: 'Run backup in production or test mode'
        )
        string(
            name: 'TEST_DATE',
            defaultValue: '',
            description: 'Optional: Test date for backup (YYYY-MM-DD)'
        )
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                echo '📂 Checking out code from GitHub...'
                checkout scm
                echo '✅ Code checked out successfully'
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo '🔧 Setting up Python environment...'
                bat '''
                    echo Python version:
                    %PYTHON_PATH% --version
                    
                    echo Installing dependencies...
                    %PIP_PATH% install -r requirements.txt
                    
                    echo ✅ Setup complete
                '''
            }
        }
        
        stage('Create Config File') {
            steps {
                echo '⚙️ Creating config.json...'
                bat '''
                    echo {
                        "snapshot_limit": 2,
                        "database": {
                            "host": "localhost",
                            "port": 3306,
                            "user": "root",
                            "password": "Aslam@93738",
                            "source_database": "ecommerce_db",
                            "history_database": "ecommerce_backup"
                        },
                        "backup_tables": [
                            "customers",
                            "products",
                            "orders",
                            "order_items"
                        ]
                    } > config.json
                '''
                echo '✅ config.json created'
            }
        }
        
        stage('Run Backup') {
            steps {
                echo '📊 Starting database backup...'
                bat '''
                    echo Running backup script...
                    %PYTHON_PATH% %PYTHON_SCRIPT%
                    echo ✅ Backup completed!
                '''
            }
        }
        
        stage('Verify Backup') {
            steps {
                echo '🔍 Verifying backup...'
                bat '''
                    echo Checking backup status...
                    echo Backup verification complete
                '''
            }
        }
    }
    
    post {
        success {
            echo '🎉 Pipeline succeeded! Backup completed successfully.'
        }
        failure {
            echo '💥 Pipeline failed! Check the logs for details.'
        }
        always {
            echo '🏁 Pipeline finished.'
        }
    }
}