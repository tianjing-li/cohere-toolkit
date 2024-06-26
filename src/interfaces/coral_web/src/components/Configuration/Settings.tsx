import { useContext, useMemo } from 'react';

import {
  Dropdown,
  DropdownOptionGroups,
  InputLabel,
  STYLE_LEVEL_TO_CLASSES,
  Slider,
  Text,
} from '@/components/Shared';
import { BannerContext } from '@/context/BannerContext';
import { useListAllDeployments, useListDeployments } from '@/hooks/deployments';
import { useSettingsDefaults } from '@/hooks/settings';
import { useParamsStore } from '@/stores';
import { cn } from '@/utils';

/**
 * @description Settings tab to adjust endpoint params like preamble and temperature.
 */
export const Settings: React.FC = () => {
  const { message: bannerMessage, setMessage } = useContext(BannerContext);
  const {
    params: { temperature, preamble, deployment, model },
    setParams,
  } = useParamsStore();
  const defaults = useSettingsDefaults();
  const { data: availableDeployments } = useListDeployments();
  const { data: allDeployments = [] } = useListAllDeployments();
  const deploymentOptions: DropdownOptionGroups = [
    {
      options: allDeployments.map(({ name }) => ({
        label: name,
        value: name,
      })),
    },
  ];
  const modelOptions = useMemo(() => {
    const selectedDeployment = allDeployments?.find(({ name }) => name === deployment);
    if (!selectedDeployment) return [];
    return [
      {
        options: selectedDeployment.models.map((model) => ({
          label: model,
          value: model,
        })),
      },
    ];
  }, [deployment]);

  const reset = () => {
    setParams({
      ...defaults,
      tools: defaults.tools,
    });
  };

  return (
    <div className="flex flex-col gap-y-6 px-5 pb-10">
      <Dropdown
        className="w-full"
        label="Deployment"
        kind="default"
        value={deployment}
        onChange={(deploymentName: string) => {
          const deployment = allDeployments.find((d) => d.name === deploymentName);
          if (availableDeployments?.every((ad) => ad.name !== deploymentName)) {
            setMessage(
              <Text as="span">
                If you wish to use <b className="font-medium">{deploymentName}</b>, please configure
                your .env file with these variables:{' '}
                <b className="font-medium">{deployment?.env_vars.join(', ')}</b>.
              </Text>
            );
          } else if (bannerMessage) {
            setMessage('');
          }
          setParams({ deployment: deploymentName });
        }}
        optionGroups={deploymentOptions}
      />
      <Dropdown
        className="w-full"
        label="Model"
        kind="default"
        value={model}
        onChange={(model: string) => setParams({ model })}
        optionGroups={modelOptions}
      />
      <Slider
        className="w-full"
        label="Temperature"
        min={0}
        max={1}
        step={0.1}
        value={temperature || 0}
        onChange={(temperature: number) => setParams({ temperature })}
        dataTestId="slider-temperature"
      />

      <InputLabel label="Preamble">
        <textarea
          value={preamble}
          placeholder="e.g. You are Coral, a large language model trained to have polite, helpful, inclusive conversations with people."
          className={cn(
            'mt-2 w-full flex-1 resize-none p-3',
            'transition ease-in-out',
            'rounded-lg border',
            'bg-marble-100',
            'border-marble-500 placeholder:text-volcanic-700 focus:border-secondary-700',
            'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900',
            STYLE_LEVEL_TO_CLASSES.p
          )}
          rows={5}
          onChange={(e) => setParams({ preamble: e.target.value })}
          data-testid="input-preamble"
        />
      </InputLabel>

      <div className="flex w-full justify-end">
        <button type="button" onClick={reset}>
          <Text
            as="span"
            className="text-secondary-800 transition ease-in-out hover:text-volcanic-900"
          >
            Reset
          </Text>
        </button>
      </div>
    </div>
  );
};
