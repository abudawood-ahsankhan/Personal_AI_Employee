/**
 * LinkedIn MCP Server - Personal AI Employee Silver Tier
 * 
 * This MCP server provides LinkedIn posting capabilities for the AI Employee.
 * It uses LinkedIn's API or browser automation for posting.
 * 
 * Setup Instructions:
 * 1. npm install
 * 2. Get LinkedIn API credentials from https://www.linkedin.com/developers/apps
 * 3. Copy .env.example to .env and fill in credentials
 * 4. Run: node index.js
 * 
 * Usage with Claude Code:
 * Configure in ~/.config/claude-code/mcp.json:
 * {
 *   "mcpServers": {
 *     "linkedin": {
 *       "command": "node",
 *       "args": ["/path/to/mcp-linkedin/index.js"],
 *       "env": {
 *         "LINKEDIN_ACCESS_TOKEN": "your_token"
 *       }
 *     }
 *   }
 * }
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// LinkedIn API configuration
const LINKEDIN_API_URL = 'https://api.linkedin.com/v2';
const ACCESS_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN;
const PERSON_URN = process.env.LINKEDIN_PERSON_URN; // e.g., 'urn:li:person:ABC123'

/**
 * Post to LinkedIn using API
 */
async function createLinkedInPost(text, visibility = 'PUBLIC') {
  if (!ACCESS_TOKEN) {
    throw new Error('LINKEDIN_ACCESS_TOKEN not configured');
  }

  try {
    const response = await axios.post(
      `${LINKEDIN_API_URL}/ugcPosts`,
      {
        author: PERSON_URN || 'urn:li:person:UNKNOWN',
        lifecycleState: 'PUBLISHED',
        specificContent: {
          'com.linkedin.ugc.ShareContent': {
            shareCommentary: {
              text: text
            },
            shareMediaCategory: 'NONE'
          }
        },
        visibility: {
          'com.linkedin.ugc.MemberNetworkVisibility': visibility
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${ACCESS_TOKEN}`,
          'Content-Type': 'application/json',
          'X-Restli-Protocol-Version': '2.0.0'
        }
      }
    );

    return {
      success: true,
      postId: response.data.id,
      message: 'Post created successfully'
    };
  } catch (error) {
    console.error('LinkedIn API Error:', error.response?.data || error.message);
    throw new Error(`Failed to create LinkedIn post: ${error.message}`);
  }
}

/**
 * Get LinkedIn profile information
 */
async function getProfile() {
  if (!ACCESS_TOKEN) {
    throw new Error('LINKEDIN_ACCESS_TOKEN not configured');
  }

  try {
    const response = await axios.get(
      `${LINKEDIN_API_URL}/me`,
      {
        headers: {
          'Authorization': `Bearer ${ACCESS_TOKEN}`
        }
      }
    );

    return {
      success: true,
      profile: response.data
    };
  } catch (error) {
    console.error('LinkedIn Profile Error:', error.response?.data || error.message);
    throw new Error(`Failed to get profile: ${error.message}`);
  }
}

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'linkedin-mcp',
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
        name: 'create_post',
        description: 'Create a new post on LinkedIn. Use this to share business updates, achievements, or professional content.',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'The content of the LinkedIn post (max 3000 characters)'
            },
            visibility: {
              type: 'string',
              enum: ['PUBLIC', 'CONNECTIONS', 'ONLY_ME'],
              description: 'Who can see the post',
              default: 'PUBLIC'
            }
          },
          required: ['text']
        }
      },
      {
        name: 'get_profile',
        description: 'Get the current LinkedIn profile information',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'create_business_update',
        description: 'Create a structured business update post with revenue/tasks info from the AI Employee dashboard',
        inputSchema: {
          type: 'object',
          properties: {
            revenue: {
              type: 'string',
              description: 'Revenue information to share'
            },
            milestones: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of milestones achieved'
            },
            gratitude: {
              type: 'string',
              description: 'Thank you message to clients/team'
            }
          },
          required: ['revenue']
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'create_post': {
        const { text, visibility = 'PUBLIC' } = args;
        
        if (!text || text.trim().length === 0) {
          throw new Error('Post text cannot be empty');
        }

        if (text.length > 3000) {
          throw new Error('Post text exceeds 3000 character limit');
        }

        const result = await createLinkedInPost(text, visibility);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ LinkedIn Post Created Successfully!\n\nPost ID: ${result.postId}\nVisibility: ${visibility}\n\nThe post is now live on your LinkedIn profile.`
            }
          ]
        };
      }

      case 'get_profile': {
        const result = await getProfile();
        
        return {
          content: [
            {
              type: 'text',
              text: `LinkedIn Profile:\n\n${JSON.stringify(result.profile, null, 2)}`
            }
          ]
        };
      }

      case 'create_business_update': {
        const { revenue, milestones = [], gratitude = '' } = args;
        
        // Format business update post
        let postText = `📊 Business Update\n\n`;
        postText += `💰 Revenue: ${revenue}\n\n`;
        
        if (milestones.length > 0) {
          postText += `🎯 Milestones Achieved:\n`;
          milestones.forEach((milestone, i) => {
            postText += `• ${milestone}\n`;
          });
          postText += '\n';
        }
        
        if (gratitude) {
          postText += `🙏 ${gratitude}\n\n`;
        }
        
        postText += `#BusinessUpdate #Entrepreneurship #Growth`;

        const result = await createLinkedInPost(postText);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Business Update Posted!\n\nPost ID: ${result.postId}\n\nContent:\n${postText}`
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
  console.error('Starting LinkedIn MCP Server...');
  console.error('LinkedIn MCP Server ready');
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('Connected to stdin/stdout transport');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
