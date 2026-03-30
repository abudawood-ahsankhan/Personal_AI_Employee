/**
 * Odoo Community ERP MCP Server - Personal AI Employee Gold Tier
 * 
 * Integrates with Odoo Community Edition via JSON-RPC API
 * Provides accounting, invoicing, and business management capabilities
 * 
 * Setup Instructions:
 * 1. Install Odoo Community Edition (local or cloud VM)
 * 2. npm install
 * 3. Copy .env.example to .env and configure
 * 4. Run: node index.js
 * 
 * Odoo JSON-RPC API Reference:
 * https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import dotenv from 'dotenv';
import CryptoJS from 'crypto-js';

dotenv.config();

// Odoo configuration
const ODOO_CONFIG = {
  url: process.env.ODOO_URL || 'http://localhost:8069',
  db: process.env.ODOO_DATABASE || 'odoo',
  username: process.env.ODOO_USERNAME || 'admin',
  password: process.env.ODOO_PASSWORD || 'admin',
  apiKey: process.env.ODOO_API_KEY || '',
};

// Session cache
let uid = null;
let sessionId = null;

/**
 * Authenticate with Odoo and get session
 */
async function authenticate() {
  try {
    const response = await axios.post(`${ODOO_CONFIG.url}/web/session/authenticate`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        db: ODOO_CONFIG.db,
        login: ODOO_CONFIG.username,
        password: ODOO_CONFIG.password,
      },
      id: 1,
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.data.result && response.data.result.uid) {
      uid = response.data.result.uid;
      sessionId = response.data.result.session_id;
      console.error('✓ Odoo authenticated');
      return true;
    }
    return false;
  } catch (error) {
    console.error('Odoo authentication error:', error.response?.data || error.message);
    return false;
  }
}

/**
 * Execute Odoo RPC call
 */
async function executeRPC(model, method, args = [], kwargs = {}) {
  if (!uid) {
    await authenticate();
  }

  try {
    const response = await axios.post(`${ODOO_CONFIG.url}/web/dataset/call_kw`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        model: model,
        method: method,
        args: args,
        kwargs: {
          ...kwargs,
          context: {
            ...kwargs.context,
            uid: uid,
          },
        },
      },
      id: Math.floor(Math.random() * 10000),
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `session_id=${sessionId}`,
      },
    });

    return response.data.result;
  } catch (error) {
    console.error(`Odoo RPC Error (${model}.${method}):`, error.response?.data || error.message);
    
    // Try to re-authenticate on session error
    if (error.response?.status === 403) {
      await authenticate();
      return executeRPC(model, method, args, kwargs);
    }
    
    throw error;
  }
}

/**
 * Create invoice in Odoo
 */
async function createInvoice(partnerId, lines, invoiceType = 'out_invoice') {
  const invoiceData = {
    move_type: invoiceType,
    partner_id: partnerId,
    invoice_line_ids: lines.map(line => [0, 0, {
      product_id: line.product_id,
      name: line.name,
      quantity: line.quantity,
      price_unit: line.price_unit,
    }]),
  };

  const result = await executeRPC('account.move', 'create', [invoiceData]);
  return result;
}

/**
 * Get invoices from Odoo
 */
async function getInvoices(domain = [], limit = 10) {
  const defaultDomain = [['move_type', 'in', ['out_invoice', 'in_invoice']]];
  const invoices = await executeRPC('account.move', 'search_read', [
    [...defaultDomain, ...domain],
    ['name', 'partner_id', 'invoice_date', 'amount_total', 'amount_residual', 'state']
  ], { limit });
  
  return invoices;
}

/**
 * Get partners (customers/vendors) from Odoo
 */
async function getPartners(domain = [], limit = 50) {
  const partners = await executeRPC('res.partner', 'search_read', [
    domain,
    ['name', 'email', 'phone', 'company_id']
  ], { limit });
  
  return partners;
}

/**
 * Create partner in Odoo
 */
async function createPartner(partnerData) {
  const result = await executeRPC('res.partner', 'create', [partnerData]);
  return result;
}

/**
 * Get products from Odoo
 */
async function getProducts(domain = [], limit = 50) {
  const products = await executeRPC('product.template', 'search_read', [
    domain,
    ['name', 'list_price', 'standard_price', 'type']
  ], { limit });
  
  return products;
}

/**
 * Register invoice payment
 */
async function registerPayment(invoiceId, amount, paymentMethod = 'manual') {
  // Create payment wizard
  const wizard = await executeRPC('account.payment.register', 'create', [{
    payment_difference_handling: 'open',
    payment_method_name: paymentMethod,
  }]);
  
  // Create payment
  const result = await executeRPC('account.payment.register', 'create_payments', [
    [invoiceId]
  ]);
  
  return result;
}

/**
 * Get accounting summary
 */
async function getAccountingSummary() {
  const totals = await executeRPC('account.move', 'read_group', [
    [['state', 'in', ['posted', 'draft']]],
    ['move_type', 'amount_total:sum', 'amount_residual:sum'],
    ['move_type']
  ]);
  
  return totals;
}

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'mcp-odoo',
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
        name: 'create_invoice',
        description: 'Create a new customer invoice in Odoo ERP',
        inputSchema: {
          type: 'object',
          properties: {
            partner_id: {
              type: 'integer',
              description: 'Customer/partner ID in Odoo'
            },
            lines: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  product_id: { type: 'integer', description: 'Product ID' },
                  name: { type: 'string', description: 'Description' },
                  quantity: { type: 'number', description: 'Quantity' },
                  price_unit: { type: 'number', description: 'Unit price' }
                },
                required: ['name', 'quantity', 'price_unit']
              },
              description: 'Invoice line items'
            },
            invoice_type: {
              type: 'string',
              enum: ['out_invoice', 'in_invoice', 'out_refund', 'in_refund'],
              default: 'out_invoice',
              description: 'Type of invoice'
            }
          },
          required: ['partner_id', 'lines']
        }
      },
      {
        name: 'get_invoices',
        description: 'Retrieve invoices from Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            domain: {
              type: 'array',
              items: { type: 'array' },
              description: 'Odoo domain filter (e.g., [["state", "=", "posted"]])'
            },
            limit: {
              type: 'integer',
              default: 10,
              description: 'Maximum number of invoices to return'
            }
          }
        }
      },
      {
        name: 'get_partners',
        description: 'Retrieve customers/vendors from Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            domain: {
              type: 'array',
              items: { type: 'array' },
              description: 'Odoo domain filter'
            },
            limit: {
              type: 'integer',
              default: 50,
              description: 'Maximum number of partners to return'
            }
          }
        }
      },
      {
        name: 'create_partner',
        description: 'Create a new partner (customer/vendor) in Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string', description: 'Partner name' },
            email: { type: 'string', description: 'Email address' },
            phone: { type: 'string', description: 'Phone number' },
            is_company: { type: 'boolean', default: true, description: 'Is a company' }
          },
          required: ['name']
        }
      },
      {
        name: 'get_products',
        description: 'Retrieve products/services from Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            domain: {
              type: 'array',
              items: { type: 'array' },
              description: 'Odoo domain filter'
            },
            limit: {
              type: 'integer',
              default: 50,
              description: 'Maximum number of products to return'
            }
          }
        }
      },
      {
        name: 'register_payment',
        description: 'Register a payment for an invoice',
        inputSchema: {
          type: 'object',
          properties: {
            invoice_id: {
              type: 'integer',
              description: 'Invoice ID (Odoo move ID)'
            },
            amount: {
              type: 'number',
              description: 'Payment amount'
            },
            payment_method: {
              type: 'string',
              enum: ['manual', 'bank', 'cash'],
              default: 'manual',
              description: 'Payment method'
            }
          },
          required: ['invoice_id', 'amount']
        }
      },
      {
        name: 'get_accounting_summary',
        description: 'Get accounting summary (totals by invoice type)',
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
      case 'create_invoice': {
        const { partner_id, lines, invoice_type = 'out_invoice' } = args;
        const invoiceId = await createInvoice(partner_id, lines, invoice_type);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Invoice created successfully!\n\nInvoice ID: ${invoiceId}\nPartner ID: ${partner_id}\nType: ${invoice_type}\nLines: ${lines.length}`
            }
          ]
        };
      }

      case 'get_invoices': {
        const { domain = [], limit = 10 } = args;
        const invoices = await getInvoices(domain, limit);
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 Invoices (${invoices.length} found):\n\n${invoices.map(inv => 
                `- ${inv.name}: ${inv.amount_total} (${inv.state})`
              ).join('\n')}`
            }
          ]
        };
      }

      case 'get_partners': {
        const { domain = [], limit = 50 } = args;
        const partners = await getPartners(domain, limit);
        
        return {
          content: [
            {
              type: 'text',
              text: `👥 Partners (${partners.length} found):\n\n${partners.map(p => 
                `- ${p.name} (${p.email || 'no email'})`
              ).join('\n')}`
            }
          ]
        };
      }

      case 'create_partner': {
        const { name, email, phone, is_company = true } = args;
        const partnerId = await createPartner({ name, email, phone, is_company });
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Partner created successfully!\n\nPartner ID: ${partnerId}\nName: ${name}\nEmail: ${email || 'N/A'}\nPhone: ${phone || 'N/A'}`
            }
          ]
        };
      }

      case 'get_products': {
        const { domain = [], limit = 50 } = args;
        const products = await getProducts(domain, limit);
        
        return {
          content: [
            {
              type: 'text',
              text: `📦 Products (${products.length} found):\n\n${products.map(p => 
                `- ${p.name}: $${p.list_price}`
              ).join('\n')}`
            }
          ]
        };
      }

      case 'register_payment': {
        const { invoice_id, amount, payment_method = 'manual' } = args;
        await registerPayment(invoice_id, amount, payment_method);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Payment registered!\n\nInvoice ID: ${invoice_id}\nAmount: $${amount}\nMethod: ${payment_method}`
            }
          ]
        };
      }

      case 'get_accounting_summary': {
        const summary = await getAccountingSummary();
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 Accounting Summary:\n\n${summary.map(s => 
                `- ${s.move_type}: Total $${s.amount_total}, Due $${s.amount_residual}`
              ).join('\n')}`
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
  console.error('Starting Odoo MCP Server...');
  console.error(`Odoo URL: ${ODOO_CONFIG.url}`);
  console.error(`Database: ${ODOO_CONFIG.db}`);
  
  // Try initial authentication
  await authenticate();
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('✓ Odoo MCP Server connected to transport');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
