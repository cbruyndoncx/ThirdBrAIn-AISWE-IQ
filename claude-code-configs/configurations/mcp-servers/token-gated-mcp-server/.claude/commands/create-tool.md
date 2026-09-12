---
allowed-tools: Write, Edit, Read
description: Create a new token-gated tool with proper protection
argument-hint: "<tool-name> <token-id> [tier]"
---

## Create Token-Gated Tool

Create a new FastMCP tool with token protection using the Radius MCP SDK.

Parameters: $ARGUMENTS

## Tool Creation Steps

1. **Parse Arguments**
   - Extract tool name, token ID, and optional tier
   - Validate token ID format
   - Determine appropriate access pattern

2. **Generate Tool Implementation**

```typescript
server.addTool({
  name: '{tool_name}',
  description: '{description} (requires token {token_id})',
  parameters: z.object({
    // Define your parameters here
    input: z.string().describe('Input data'),
    options: z.object({
      format: z.enum(['json', 'text']).optional(),
      verbose: z.boolean().optional()
    }).optional(),
    __evmauth: z.any().optional().describe('Authentication proof')
  }),
  handler: radius.protect({token_id}, async (args) => {
    // Tool implementation
    try {
      // Process the input
      const result = await process{ToolName}(args.input, args.options);
      
      // Return MCP-formatted response
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      throw new Error(`{tool_name} failed: ${error.message}`);
    }
  })
});
```

3. **Add to Appropriate Tier**
   - Map to correct token tier
   - Update TOOL_REQUIREMENTS mapping
   - Document access requirements

4. **Create Test Case**
   - Unit test for the tool
   - Auth flow test
   - Error handling test

5. **Update Documentation**
   - Add to tool registry
   - Document parameters
   - Include usage examples

## Generate Complete Tool

Based on the arguments provided, create:

1. Tool implementation file
2. Test file
3. Documentation update
4. Integration with existing server

The tool should follow FastMCP best practices and properly integrate with the Radius MCP SDK for token protection.
