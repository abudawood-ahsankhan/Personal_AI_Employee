/**
 * Twitter (X) MCP Server - Personal AI Employee Gold Tier
 * 
 * Integrates with Twitter API v2 for posting and analytics
 * 
 * Setup Instructions:
 * 1. Create Twitter Developer Account at https://developer.twitter.com/
 * 2. Create a Project and App
 * 3. Get API Key, API Secret, Access Token, and Access Token Secret
 * 4. npm install
 * 5. Copy .env.example to .env
 * 6. Run: node index.js
 * 
 * Twitter API v2 Reference:
 * https://developer.twitter.com/en/docs/twitter-api
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { TwitterApi } from 'twitter-api-v2';
import dotenv from 'dotenv';

dotenv.config();

// Twitter configuration
const TWITTER_CONFIG = {
  appKey: process.env.TWITTER_API_KEY || '',
  appSecret: process.env.TWITTER_API_SECRET || '',
  accessToken: process.env.TWITTER_ACCESS_TOKEN || '',
  accessSecret: process.env.TWITTER_ACCESS_SECRET || '',
};

// Initialize Twitter client
let twitterClient = null;

function getTwitterClient() {
  if (!twitterClient) {
    twitterClient = new TwitterApi({
      appKey: TWITTER_CONFIG.appKey,
      appSecret: TWITTER_CONFIG.appSecret,
      accessToken: TWITTER_CONFIG.accessToken,
      accessSecret: TWITTER_CONFIG.accessSecret,
    });
  }
  return twitterClient;
}

/**
 * Post a tweet
 */
async function postTweet(text, mediaIds = []) {
  const client = getTwitterClient();
  
  const tweetParams = {
    text: text,
  };

  if (mediaIds.length > 0) {
    tweetParams.media = {
      media_ids: mediaIds,
    };
  }

  const response = await client.v2.tweet(tweetParams);
  return response.data;
}

/**
 * Post a thread of tweets
 */
async function postThread(tweets) {
  const client = getTwitterClient();
  const results = [];
  let lastTweetId = null;

  for (const tweetText of tweets) {
    const tweetParams = {
      text: tweetText,
    };

    if (lastTweetId) {
      tweetParams.reply = {
        in_reply_to_tweet_id: lastTweetId,
      };
    }

    const response = await client.v2.tweet(tweetParams);
    results.push(response.data);
    lastTweetId = response.data.id;
  }

  return results;
}

/**
 * Upload media to Twitter
 */
async function uploadMedia(mediaUrl, mediaType = 'image') {
  const client = getTwitterClient();
  
  // Download media
  const axios = (await import('axios')).default;
  const response = await axios.get(mediaUrl, { responseType: 'arraybuffer' });
  
  // Upload to Twitter
  const uploadResponse = await client.v1.uploadMedia(response.data, {
    mimeType: mediaType === 'image' ? 'image/png' : 'video/mp4',
  });

  return uploadResponse.media_id_string;
}

/**
 * Get user timeline
 */
async function getTimeline(username, limit = 5) {
  const client = getTwitterClient();
  
  // Get user ID from username
  const user = await client.v2.userByUsername(username);
  const userId = user.data.id;

  // Get tweets
  const tweets = await client.v2.userTimeline(userId, {
    max_results: limit,
    'tweet.fields': ['created_at', 'public_metrics', 'text'],
  });

  return tweets.data;
}

/**
 * Get tweet metrics
 */
async function getTweetMetrics(tweetId) {
  const client = getTwitterClient();
  
  const tweet = await client.v2.singleTweet(tweetId, {
    'tweet.fields': ['public_metrics', 'created_at', 'text'],
  });

  return tweet.data;
}

/**
 * Get account metrics summary
 */
async function getAccountMetrics(username) {
  const client = getTwitterClient();
  
  // Get user info
  const user = await client.v2.userByUsername(username, {
    'user.fields': ['public_metrics', 'created_at', 'description'],
  });

  return user.data;
}

/**
 * Search tweets
 */
async function searchTweets(query, limit = 10) {
  const client = getTwitterClient();
  
  const tweets = await client.v2.search(query, {
    max_results: limit,
    'tweet.fields': ['created_at', 'public_metrics', 'text', 'author_id'],
  });

  return tweets.data;
}

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'mcp-twitter',
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
        name: 'post_tweet',
        description: 'Post a tweet to Twitter/X',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Tweet text (max 280 characters)'
            },
            media_urls: {
              type: 'array',
              items: { type: 'string' },
              description: 'Optional media URLs to attach'
            }
          },
          required: ['text']
        }
      },
      {
        name: 'post_thread',
        description: 'Post a thread of tweets',
        inputSchema: {
          type: 'object',
          properties: {
            tweets: {
              type: 'array',
              items: { type: 'string' },
              description: 'Array of tweet texts for the thread'
            }
          },
          required: ['tweets']
        }
      },
      {
        name: 'get_timeline',
        description: 'Get recent tweets from a user',
        inputSchema: {
          type: 'object',
          properties: {
            username: {
              type: 'string',
              description: 'Twitter username (without @)'
            },
            limit: {
              type: 'integer',
              default: 5,
              description: 'Number of tweets to retrieve'
            }
          },
          required: ['username']
        }
      },
      {
        name: 'get_tweet_metrics',
        description: 'Get metrics for a specific tweet',
        inputSchema: {
          type: 'object',
          properties: {
            tweet_id: {
              type: 'string',
              description: 'Tweet ID'
            }
          },
          required: ['tweet_id']
        }
      },
      {
        name: 'get_account_metrics',
        description: 'Get account metrics (followers, following, etc.)',
        inputSchema: {
          type: 'object',
          properties: {
            username: {
              type: 'string',
              description: 'Twitter username (without @)'
            }
          },
          required: ['username']
        }
      },
      {
        name: 'search_tweets',
        description: 'Search for tweets by query',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query'
            },
            limit: {
              type: 'integer',
              default: 10,
              description: 'Number of tweets to retrieve'
            }
          },
          required: ['query']
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
      case 'post_tweet': {
        const { text, media_urls = [] } = args;
        
        // Upload media if provided
        let mediaIds = [];
        if (media_urls.length > 0) {
          for (const url of media_urls) {
            try {
              const mediaId = await uploadMedia(url);
              mediaIds.push(mediaId);
            } catch (error) {
              console.error('Media upload error:', error.message);
            }
          }
        }
        
        const tweet = await postTweet(text, mediaIds);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Tweet posted successfully!\n\nTweet ID: ${tweet.id}\nText: ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}\n\nView: https://twitter.com/user/status/${tweet.id}`
            }
          ]
        };
      }

      case 'post_thread': {
        const { tweets } = args;
        const results = await postThread(tweets);
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Thread posted successfully!\n\nTweets posted: ${results.length}\nFirst tweet ID: ${results[0].id}\n\nView thread: https://twitter.com/user/status/${results[0].id}`
            }
          ]
        };
      }

      case 'get_timeline': {
        const { username, limit = 5 } = args;
        const tweets = await getTimeline(username, limit);
        
        return {
          content: [
            {
              type: 'text',
              text: `📱 Recent tweets from @${username}:\n\n${tweets.map(t => 
                `- ${t.text.substring(0, 100)}... (❤️ ${t.public_metrics.like_count}, 🔄 ${t.public_metrics.retweet_count})`
              ).join('\n')}`
            }
          ]
        };
      }

      case 'get_tweet_metrics': {
        const { tweet_id } = args;
        const metrics = await getTweetMetrics(tweet_id);
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 Tweet Metrics:\n\nLikes: ${metrics.public_metrics.like_count}\nRetweets: ${metrics.public_metrics.retweet_count}\nReplies: ${metrics.public_metrics.reply_count}\nImpressions: ${metrics.public_metrics.impression_count}`
            }
          ]
        };
      }

      case 'get_account_metrics': {
        const { username } = args;
        const account = await getAccountMetrics(username);
        
        return {
          content: [
            {
              type: 'text',
              text: `📊 @${username} Account Metrics:\n\nFollowers: ${account.public_metrics.followers_count}\nFollowing: ${account.public_metrics.following_count}\nTweets: ${account.public_metrics.tweet_count}\nListed: ${account.public_metrics.listed_count}`
            }
          ]
        };
      }

      case 'search_tweets': {
        const { query, limit = 10 } = args;
        const tweets = await searchTweets(query, limit);
        
        return {
          content: [
            {
              type: 'text',
              text: `🔍 Search results for "${query}":\n\n${tweets.map(t => 
                `- @${t.author_id}: ${t.text.substring(0, 100)}...`
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
  console.error('Starting Twitter (X) MCP Server...');
  
  if (!TWITTER_CONFIG.appKey) {
    console.error('⚠️  Warning: TWITTER_API_KEY not set');
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('✓ Twitter MCP Server connected');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
