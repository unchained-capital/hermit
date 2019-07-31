pipeline {
  agent any
  environment {
    CI = 'true'
  }
  stages {
    stage('Build') {
      steps {
        sh '''
          # Make application dependencies first so the .virtualenv exists.
          make python-dependencies
          . .virtualenv/bin/activate
          make package
        '''
      }
    }
    stage('Test') {
      steps {
        sh '''
          . .virtualenv/bin/activate
          python setup.py install
          make lint
          make test 
        '''
      }
    }
    stage('Publish') {
      when {
        branch 'master-or-maybe-never'
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'tbd', passwordVarable: 'PYPI_PASSWORD', usernameVariable: 'PYPI_USERNAME')]) {
          sh '''
            . ./environment.sh
            make upload
          '''
        }
      }
    }
  }
}


