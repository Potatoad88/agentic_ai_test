import { nanoid } from 'nanoid';

import { WorkflowNodeType } from '../constants';
import { FlowNodeRegistry } from '../../typings';
import iconTool from '../../assets/icon-tool.jpg';

let index = 0;
export const ToolNodeRegistry: FlowNodeRegistry = {
  type: WorkflowNodeType.Tool,
  info: {
    icon: iconTool,
    description:
      'This node represents a tool that can be connected to an AI agent node. The agent can use this tool to perform specific actions or access external functionalities.',
  },
  meta: {
    size: {
      width: 340,
      height: 220,
    },
  },
  onAdd() {
    return {
      id: `tool_${nanoid(5)}`,
      type: 'tool',
      data: {
        title: `Tool_${++index}`,
        inputsValues: {
          toolName: {
            type: 'constant',
            content: '',
          },
          toolDescription: {
            type: 'template',
            content: '',
          },
        },
        inputs: {
          type: 'object',
          required: ['toolName', 'toolDescription'],
          properties: {
            toolName: {
              type: 'string',
              description: 'The name of the tool.',
              enum: ['Tool1', 'Tool2', 'Tool3'],
            },
            toolDescription: {
              type: 'string',
              description: 'A description of what the tool does.',
            },
          },
        },
        outputs: {
          type: 'object',
          properties: {
            toolResult: { type: 'string', description: 'The result or output from the tool.' },
          },
        },
      },
    };
  },
};
