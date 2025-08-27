module.exports = {
  apps: [
    {
      name: 'tinderlike-backend',
      script: 'run.py',
      cwd: '/var/www/tinderlike',
      interpreter: '/var/www/tinderlike/venv/bin/python',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      },
      error_file: '/var/log/tinderlike/backend-error.log',
      out_file: '/var/log/tinderlike/backend-out.log',
      log_file: '/var/log/tinderlike/backend-combined.log',
      time: true
    }
  ],

  deploy: {
    production: {
      user: 'ubuntu',
      host: 'your-ec2-public-ip',  // Replace with your EC2 public IP
      ref: 'origin/main',
      repo: 'your-github-repo-url',  // Replace with your GitHub repo URL
      path: '/var/www/tinderlike',
      'pre-deploy-local': '',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
};
