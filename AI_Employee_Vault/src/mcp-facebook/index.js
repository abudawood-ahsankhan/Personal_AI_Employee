/**
 * Facebook/Instagram MCP Server - Personal AI Employee Gold Tier
 * 
 * Integrates with Meta Graph API for Facebook and Instagram posting
 * 
 * Setup Instructions:
 * 1. Create Meta App at https://developers.facebook.com/
 * 2. Get Page Access Token and Instagram Business Account ID
 * 3. npm install
 * 4. Copy .env.example to .env
 * 5. Run: node index.js
 * 
 * Graph API Reference:
 * https://developers.facebook.com/docs/graph-api
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

// Meta configuration
const META_CONFIG = {
  accessToken: process.env.FACEBOOK_ACCESS_TOKEN || '',
  pageId: process.env.FACEBOOK_PAGE_ID || '',
  instagramAccountId: process.env.INSTAGRAM_ACCOUNT_ID || '',
  apiVersion: 'v18.0',
};

const GRAPH_API_URL = `https://graph.facebook.com/${META_CONFIG.apiVersion}`;

/**
 * Post to Facebook Page
 */
async function postToFacebook(message, link = null, photoUrl = null) {
  const params = {
    message: message,
    access_token: META_CONFIG.accessToken,
  };

  if (link) {
    params.link = link;
  }

  if (photoUrl) {
    params.url = photoUrl;
  }

  const response = await axios.post(
    `${GRAPH_API_URL}/${META_CONFIG.pageId}/feed`,
    params
  );

  return response.data;
}

/**
 * Post to Instagram
 */
async function postToInstagram(caption, imageUrl = null, mediaType = 'IMAGE') {
  // Step 1: Create media container
  const containerParams = {
    image_url: imageUrl,
    caption: caption,
    access_token: META_CONFIG.accessToken,
  };

  const containerResponse = await axios.post(
    `${GRAPH_API_URL}/${META_CONFIG.instagramAccountId}/media`,
    containerParams
  );

  const creationId = containerResponse.data.id;

  // Wait for media processing
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Step 2: Publish the media
  const publishParams = {
    creation_id: creationId,
    access_token: META_CONFIG.accessToken,
  };

  const publishResponse = await axios.post(
    `${GRAPH_API_URL}/${META_CONFIG.instagramAccountId}/media_publish`,
    publishParams
  );

  return publishResponse.data;
}

/**
 * Get Facebook Page insights
 */
async function getFacebookInsights(metricNames = ['page_impressions', 'page_engaged_users']) {
  const response = await axios.get(
    `${GRAPH_API_URL}/${META_CONFIG.pageId}/insights`,
    {
      params: {
        metric: metricNames.join(','),
        access_token: META_CONFIG.accessToken,
      },
    }
  );

  return response.data;
}

/**
 * Get Instagram insights
 */
async function getInstagramInsights(metricNames = ['impressions', 'reach', 'profile_views']) {
  const response = await axios.get(
    `${GRAPH_API_URL}/${META_CONFIG.instagramAccountId}/insights`,
    {
      params: {
        metric: metricNames.join(','),
        access_token: META_CONFIG.accessToken,
      },
    }
  );

  return response.data;
}

/**
 * Get recent posts
 */
async function getRecentPosts(platform = 'facebook', limit = 5) {
  const endpoint = platform === 'facebook' 
    ? `${META_CONFIG.pageId}/posts`
    : `${META_CONFIG.instagramAccountId}/media`;

  const response = await axios.get(
    `${GRAPH_API_URL}/${endpoint}`,
    {
      params: {
        limit: limit,
        fields: platform === 'facebook' 
          ? 'message,created_time,permalink_url,shares,reactions.summary(true)'
          : 'caption,timestamp,permalink,like_count,comments_count',
        access_token: META_CONFIG.accessToken,
      },
    }
  );

  return response.data;
}

/**
 * Generate social media summary
 */
async function generateSummary() {
  try {
    const [fbInsights, igInsights, fbPosts, igPosts] = await Promise.all([
      getFacebookInsights().catch(() => null),
      getInstagramInsights().catch(() => null),
      getRecentPosts('facebook', 3).catch(() => null),
      getRecentPosts('instagram', 3).catch(() => null),
    ]);

    return {
      facebook: {
        insights: fbInsights,
        recent_posts: fbPosts,
      },
      instagram: {
        insights: igInsights,
        recent_posts: igPosts,
      },
    };
  } catch (error) {
    console.error('Error generating summary:', error.message);
    return null;
  }
}

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'mcp-facebook',
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
        name: 'post_to_facebook',
        description: 'Create a post on Facebook Page',
        inputSchema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'Post message content'
            },
            link: {
              type: 'string',
              description: 'Optional link to share'
            },
            photo_url: {
              type: 'string',
              description: 'Optional photo URL to share'
            }
          },
          required: ['message']
        }
      },
      {
        name: 'post_to_instagram',
        description: 'Create a post on Instagram Business account',
        inputSchema: {
          type: 'object',
          properties: {
            caption: {
              type: 'string',
              description: 'Instagram caption'
            },
            image_url: {
              type: 'string',
              description: 'Image URL to post'
            },
            media_type: {
              type: 'string',
              enum: ['IMAGE', 'CAROUSEL', 'REELS'],
              default: 'IMAGE',
              description: 'Type of media'
            }
          },
          required: ['caption', 'image_url']
        }
      },
      {
        name: 'get_facebook_insights',
        description: 'Get Facebook Page analytics/insights',
        inputSchema: {
          type: 'object',
          properties: {
            metrics: {
              type: 'array',
              items: { type: 'string' },
              default: ['page_impressions', 'page_engaged_users'],
              description: 'Metrics to retrieve'
            }
          }
        }
      },
      {
        name: 'get_instagram_insights',
        description: 'Get Instagram account analytics/insights',
        inputSchema: {
          type: 'object',
          properties: {
            metrics: {
              type: 'array',
              items: { type: 'string' },
              default: ['impressions', 'reach', 'profile_views'],
              description: 'Metrics to retrieve'
            }
          }
        }
      },
      {
        name: 'get_recent_posts',
        description: 'Get recent posts from Facebook or Instagram',
        inputSchema: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              enum: ['facebook', 'instagram'],
              description: 'Platform to get posts from'
            },
            limit: {
              type: 'integer',
              default: 5,
              description: 'Number of posts to retrieve'
            }
          },
          required: ['platform']
        }
      },
      {
        name: 'generate_social_summary',
        description: 'Generate comprehensive social media summary for both platforms',
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
      case 'post_to_facebook': {
        const { message, link = null, photo_url = null } = args;
        const response = await postToFacebook(message, link, photo_url);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Facebook post created successfully!\n\nPost ID: ${response.id}\n\nYour post is now live on your Facebook Page.`
            }
          ]
        };
      }

      case 'post_to_instagram': {
        const { caption, image_url, media_type = 'IMAGE' } = args;
        const response = await postToInstagram(caption, image_url, media_type);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Instagram post created successfully!\n\nPost ID: ${response.id}\n\nYour post is now live on Instagram.`
            }
          ]
        };
      }

      case 'get_facebook_insights': {
        const { metrics = ['page_impressions', 'page_engaged_users'] } = args;
        const insights = await getFacebookInsights(metrics);
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 Facebook Insights:\n\n${JSON.stringify(insights, null, 2)}`
            }
          ]
        };
      }

      case 'get_instagram_insights': {
        const { metrics = ['impressions', 'reach', 'profile_views'] } = args;
        const insights = await getInstagramInsights(metrics);
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 Instagram Insights:\n\n${JSON.stringify(insights, null, 2)}`
            }
          ]
        };
      }

      case 'get_recent_posts': {
        const { platform, limit = 5 } = args;
        const posts = await getRecentPosts(platform, limit);
        
        return {
          content: [
            {
              type: 'text',
              text: `📱 Recent ${platform} posts (${posts.data?.length || 0}):\n\n${JSON.stringify(posts, null, 2)}`
            }
          ]
        };
      }

      case 'generate_social_summary': {
        const summary = await generateSummary();
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 Social Media Summary:\n\n${JSON.stringify(summary, null, 2)}`
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
          text: `❌ Error: ${error.message}\n\nStack: ${error.stack}`
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
  console.error('Starting Facebook/Instagram MCP Server...');
  console.error(`Page ID: ${META_CONFIG.pageId}`);
  console.error(`Instagram Account ID: ${META_CONFIG.instagramAccountId}`);
  
  if (!META_CONFIG.accessToken) {
    console.error('⚠️  Warning: FACEBOOK_ACCESS_TOKEN not set');
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('✓ Facebook/Instagram MCP Server connected');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
