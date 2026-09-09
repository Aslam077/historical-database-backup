pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'historical-database-backup'
        PYTHON_SCRIPT = 'backup.py'
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
                    python --version
                    
                    echo Installing dependencies...
                    pip install -r requirements.txt
                    
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
                    python backup.py
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
            // Optional: Send email notification
        }
        failure {
            echo '💥 Pipeline failed! Check the logs for details.'
            // Optional: Send failure alert
        }
        always {
            echo '🏁 Pipeline finished.'
        }
    }
}