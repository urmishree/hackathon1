import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    proxy: { // reverse proxy configuration in javascript/ pls change to python equivalent
      '/api/send-email': {
        target: 'https://anand-outskill.app.n8n.cloud/',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/generate/, 'webhook/a7c289d5-5b98-4105-b456-8e69fdaa1ea5'),
      },
      '/api/send-email-prod': {
        target: 'https://anand-outskill.app.n8n.cloud/',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/publish/, '/webhook-test/a7c289d5-5b98-4105-b456-8e69fdaa1ea5'),
      }
    }
  }
});

// Full email sending URL:
"https://anand-outskill.app.n8n.cloud/webhook/a7c289d5-5b98-4105-b456-8e69fdaa1ea5"


// Sample json to be sent to the above URL
{
  "to": [
    "grader_vaguely921@simplelogin.com"
  ],
  "cc": [
    "ccperson1@example.com",
    "ccperson2@example.com"
  ],
  "subject": "reg: Your car is ready for pick up",
  "body": "Hello,\n\nAn ambulance has been dispatched to your location. Additionally, your car will be picked up for towing in 15 minutes and will arrive at the service centre within 45 minutes.\n\nStay safe,\nSupport Team"
}

