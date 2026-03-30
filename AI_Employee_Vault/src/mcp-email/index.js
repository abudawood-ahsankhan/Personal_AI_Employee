/**
 * Email MCP Server - Personal AI Employee Gold Tier
 * 
 * Sends emails via SMTP (Gmail, Outlook, or custom SMTP)
 * 
 * Setup Instructions:
 * 1. npm install
 * 2. Copy .env.example to .env
 * 3. Configure SMTP settings
 * 4. Run: node index.js
 * 
 * For Gmail:
 * - Enable 2FA
 * - Create App Password: https://myaccount.google.com/apppasswords
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import nodemailer from 'nodemailer';
import dotenv from 'dotenv';

dotenv.config();

// Email configuration
const EMAIL_CONFIG = {
  smtp: {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT) || 587,
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
      user: process.env.SMTP_USER || '',
      pass: process.env.SMTP_PASSWORD || '',
    },
  },
  from: process.env.EMAIL_FROM || process.env.SMTP_USER || '',
  dryRun: process.env.DRY_RUN === 'true',
};

// Create transporter
const transporter = nodemailer.createTransport({
  host: EMAIL_CONFIG.smtp.host,
  port: EMAIL_CONFIG.smtp.port,
  secure: EMAIL_CONFIG.smtp.secure,
  auth: EMAIL_CONFIG.smtp.auth,
});

/**
 * Send email
 */
async function sendEmail(to, subject, text, html = null, cc = [], bcc = [], attachments = []) {
  const mailOptions = {
    from: EMAIL_CONFIG.from,
    to: Array.isArray(to) ? to.join(', ') : to,
    subject: subject,
    text: text,
    html: html || text.replace(/\n/g, '<br>'),
    cc: cc,
    bcc: bcc,
    attachments: attachments,
  };

  if (EMAIL_CONFIG.dryRun) {
    console.log('DRY RUN: Would send email to:', to);
    return {
      messageId: 'dry-run-' + Date.now(),
      dryRun: true,
    };
  }

  const info = await transporter.sendMail(mailOptions);
  return {
    messageId: info.messageId,
    accepted: info.accepted,
    rejected: info.rejected,
  };
}

/**
 * Send invoice email
 */
async function sendInvoiceEmail(to, invoiceNumber, amount, invoicePdfPath, body = null) {
  const subject = `Invoice #${invoiceNumber}`;
  const text = body || `Dear Customer,\n\nPlease find attached invoice #${invoiceNumber} for $${amount}.\n\nThank you for your business!`;
  
  return sendEmail(to, subject, text, null, [], [], [{
    filename: `Invoice_${invoiceNumber}.pdf`,
    path: invoicePdfPath,
  }]);
}

/**
 * Send bulk email (with rate limiting)
 */
async function sendBulkEmail(recipients, subject, text, delayMs = 1000) {
  const results = [];
  
  for (const recipient of recipients) {
    try {
      const result = await sendEmail(recipient, subject, text);
      results.push({ email: recipient, success: true, ...result });
      
      // Rate limiting
      if (delayMs > 0) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    } catch (error) {
      results.push({ email: recipient, success: false, error: error.message });
    }
  }
  
  return results;
}

/**
 * Verify email configuration
 */
async function verifyConfig() {
  try {
    await transporter.verify();
    return { valid: true, message: 'SMTP configuration verified' };
  } catch (error) {
    return { valid: false, message: error.message };
  }
}

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'mcp-email',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'send_email',
        description: 'Send an email via SMTP',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address (or comma-separated list)'
            },
            subject: {
              type: 'string',
              description: 'Email subject'
            },
            text: {
              type: 'string',
              description: 'Email body (plain text)'
            },
            html: {
              type: 'string',
              description: 'Email body (HTML, optional)'
            },
            cc: {
              type: 'array',
              items: { type: 'string' },
              description: 'CC recipients'
            },
            bcc: {
              type: 'array',
              items: { type: 'string' },
              description: 'BCC recipients'
            }
          },
          required: ['to', 'subject', 'text']
        }
      },
      {
        name: 'send_invoice_email',
        description: 'Send an invoice email with PDF attachment',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Customer email address'
            },
            invoice_number: {
              type: 'string',
              description: 'Invoice number'
            },
            amount: {
              type: 'number',
              description: 'Invoice amount'
            },
            invoice_pdf_path: {
              type: 'string',
              description: 'Path to invoice PDF file'
            },
            body: {
              type: 'string',
              description: 'Custom email body (optional)'
            }
          },
          required: ['to', 'invoice_number', 'amount', 'invoice_pdf_path']
        }
      },
      {
        name: 'send_bulk_email',
        description: 'Send email to multiple recipients with rate limiting',
        inputSchema: {
          type: 'object',
          properties: {
            recipients: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of email addresses'
            },
            subject: {
              type: 'string',
              description: 'Email subject'
            },
            text: {
              type: 'string',
              description: 'Email body'
            },
            delay_ms: {
              type: 'integer',
              default: 1000,
              description: 'Delay between emails (ms) for rate limiting'
            }
          },
          required: ['recipients', 'subject', 'text']
        }
      },
      {
        name: 'verify_email_config',
        description: 'Verify SMTP configuration is working',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;
    
    switch (name) {
      case 'send_email': {
        const { to, subject, text, html, cc = [], bcc = [] } = args;
        const response = await sendEmail(to, subject, text, html, cc, bcc);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Email sent successfully!\n\nTo: ${to}\nSubject: ${subject}\nMessage ID: ${response.messageId}\n${response.dryRun ? '(DRY RUN - not actually sent)' : ''}`
            }
          ]
        };
      }

      case 'send_invoice_email': {
        const { to, invoice_number, amount, invoice_pdf_path, body } = args;
        const response = await sendInvoiceEmail(to, invoice_number, amount, invoice_pdf_path, body);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Invoice email sent!\n\nTo: ${to}\nInvoice: #${invoice_number}\nAmount: $${amount}\nMessage ID: ${response.messageId}`
            }
          ]
        };
      }

      case 'send_bulk_email': {
        const { recipients, subject, text, delay_ms = 1000 } = args;
        const results = await sendBulkEmail(recipients, subject, text, delay_ms);
        
        const successCount = results.filter(r => r.success).length;
        const failCount = results.filter(r => !r.success).length;
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Bulk email complete!\n\nTotal: ${recipients.length}\nSuccessful: ${successCount}\nFailed: ${failCount}\n\nResults:\n${results.map(r => 
                `- ${r.email}: ${r.success ? '✓' : '✗'}${r.error ? ' ' + r.error : ''}`
              ).join('\n')}`
            }
          ]
        };
      }

      case 'verify_email_config': {
        const result = await verifyConfig();
        
        return {
          content: [
            {
              type: 'text',
              text: result.valid 
                ? `✅ ${result.message}` 
                : `❌ Configuration error: ${result.message}`
            }
          ]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `❌ Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

/**
 * Start the MCP server
 */
async function main() {
  console.error('Starting Email MCP Server...');
  console.error(`SMTP Host: ${EMAIL_CONFIG.smtp.host}`);
  console.error(`From: ${EMAIL_CONFIG.from}`);
  console.error(`Dry Run: ${EMAIL_CONFIG.dryRun}`);
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('✓ Email MCP Server connected');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
