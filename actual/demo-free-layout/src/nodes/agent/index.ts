import { nanoid } from 'nanoid';

import { WorkflowNodeType } from '../constants';
import { FlowNodeRegistry } from '../../typings';
import iconAgent from '../../assets/icon-agent.jpg';

let index = 0;
export const AgentNodeRegistry: FlowNodeRegistry = {
  type: WorkflowNodeType.Agent,
  info: {
    icon: iconAgent,
    description:
      'This node represents an AI agent that can perform a user-specified task. The user can input the specific task or instruction for the agent to execute.',
  },
  meta: {
    size: {
      width: 360,
      height: 340,
    },
  },
  onAdd() {
    return {
      id: `agent_${nanoid(5)}`,
      type: 'agent',
      data: {
        title: `Agent_${++index}`,
        inputsValues: {
          name: {
            type: 'template',
            content: ``,
          },
          task: {
            type: 'template',
            content: '',
          },
          modelType: {
            type: 'constant',
            content: 'gemini',
          },
        },
        inputs: {
          type: 'object',
          required: ['name', 'task', 'modelType'],
          properties: {
            name: {
              type: 'string',
              description: 'The name of the agent.',
            },
            task: {
              type: 'string',
              description: 'The specific task or instruction for the agent to perform.',
            },
            modelType: {
              type: 'string',
              description: 'The type of model the agent will use, e.g., "gemini".',
            },
          },
        },
        outputs: {
          type: 'object',
          properties: {
            result: { type: 'string' },
          },
        },
      },
    };
  },
};
