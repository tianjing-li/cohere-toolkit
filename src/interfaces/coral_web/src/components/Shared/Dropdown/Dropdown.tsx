import { Listbox } from '@headlessui/react';
import { Fragment, useMemo, useState } from 'react';

import { Icon, Input, InputLabel, Text } from '@/components/Shared';
import { cn } from '@/utils';

type Kind = 'default' | 'cell';

export type DropdownOption = {
  value: string;
  label?: string;
  description?: string;
};
export type DropdownOptionGroups = {
  title?: string;
  options: DropdownOption[];
}[];

type Props = {
  optionGroups: DropdownOptionGroups;
  label?: string;
  placeholder?: string;
  value?: string | null;
  kind?: Kind;
  disabled?: boolean;
  tooltipLabel?: React.ReactNode;
  description?: string;
  joint?: 'left' | 'right';
  className?: string;
  onChange?: (value: any) => void;
  searchable?: boolean;
  dataTestId?: string;
};

/**
 * This component renders a standard dropdown. There are two kinds:
 * - default - dropdown with borders only around the dropdown itself
 * - cell - dropdown with borders surrounding the dropdown and the label
 *
 * Refer to Storybook for a better illustration.
 */
export const Dropdown: React.FC<Props> = ({
  optionGroups,
  label,
  tooltipLabel,
  placeholder = 'Select an option',
  value,
  kind = 'cell',
  disabled = false,
  description = '',
  joint,
  className = '',
  onChange,
  searchable = false,
  dataTestId,
}) => {
  const roundedClasses = cn({
    'rounded-t-lg': !joint,
    'rounded-l-lg rounded-r-none': joint === 'left',
    'rounded-r-lg rounded-l-none': joint === 'right',
  });
  const borderClasses = cn(roundedClasses, {
    border: !joint,
    'border-l border-t border-b': joint === 'left',
    'border-r border-t border-b': joint === 'right',
  });

  const [searchTerm, setSearchTerm] = useState('');

  const options = useMemo(
    () =>
      optionGroups.filter((group) => {
        if (!searchable || !searchTerm) {
          return true;
        }
        return group.options.some(
          (option) =>
            option.label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            option.value?.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }),
    [optionGroups, searchTerm]
  );

  const findValueOption = (value: string) => {
    for (let i = 0; i < optionGroups.length; i++) {
      const option = optionGroups[i].options.find((o) => o.value === value);

      if (option) {
        return { label: option.label ?? value, description: option.description };
      }
    }
    return { label: value, description: undefined };
  };

  const valueLabel = useMemo(() => {
    if (value) {
      return findValueOption(value).label;
    }
  }, [value, optionGroups]);

  const valueDescription = useMemo(() => {
    if (value) {
      return findValueOption(value).description;
    }
  }, [value, optionGroups]);

  const onChangeListBox = (value: any) => {
    setSearchTerm('');
    onChange?.(value);
  };

  return (
    <div className={cn(className)}>
      {kind === 'default' && label && (
        <InputLabel className="mb-2" label={label} tooltipLabel={tooltipLabel} />
      )}
      <Listbox
        value={value}
        onChange={onChangeListBox}
        disabled={disabled}
        as="div"
        className="relative"
      >
        {({ open }) => (
          <div
            className={cn(
              roundedClasses,
              borderClasses,
              'border-marble-500 bg-marble-100 hover:bg-marble-200',
              {
                'rounded-b-lg': !open,
                'rounded-bl-none rounded-br-none': open,
              }
            )}
          >
            <Listbox.Button
              className={cn(
                'relative flex w-full items-center justify-between disabled:cursor-not-allowed',
                'rounded-lg focus:outline-none focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900',
                {
                  'px-3 py-4': kind === 'default' || !label,
                  'px-3 pb-2.5 pt-7': kind === 'cell' && label,
                }
              )}
              data-testid={dataTestId}
            >
              {kind === 'cell' && label && (
                <InputLabel
                  className="absolute left-0 top-0 w-fit pl-3 pt-2.5"
                  label={label}
                  tooltipLabel={tooltipLabel}
                />
              )}
              <Text
                as="div"
                className={cn('mr-2 w-full truncate text-left', {
                  'text-volcanic-800': value === undefined,
                })}
              >
                {valueLabel ?? placeholder}{' '}
                {valueDescription && (
                  <Text as="span" className="text-volcanic-600">
                    ({valueDescription})
                  </Text>
                )}
              </Text>
              <Icon name="chevron-down" />
            </Listbox.Button>

            <Listbox.Options
              className={cn(
                'absolute left-0',
                'max-h-80 w-full overflow-y-auto bg-marble-100',
                'rounded-b-lg border border-marble-500',
                'z-dropdown',
                'focus:outline-none focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900'
              )}
            >
              {searchable && (
                <div className="sticky top-0 border-b border-marble-500 bg-white">
                  <section className="p-3">
                    <Input
                      placeholder="filter model"
                      className="m-0"
                      size="sm"
                      kind="default"
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </section>

                  {options.length === 0 && searchTerm !== '' && (
                    <>
                      <hr className="border-marble-500" />
                      <Text className="p-4">No results found</Text>
                    </>
                  )}
                </div>
              )}

              {options.map((group, i) => (
                <Fragment key={i}>
                  {group.title && (
                    <Text
                      key={group.title}
                      styleAs="overline"
                      className={cn('mx-3 py-3 font-medium', {
                        'border-b border-marble-500':
                          i !== optionGroups.length - 1 || group.options.length > 0,
                      })}
                    >
                      {group.title}
                    </Text>
                  )}
                  {group.options
                    .filter((option) => {
                      if (!searchable || !searchTerm) {
                        return true;
                      }
                      return (
                        option.label?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        option.value?.toLowerCase().includes(searchTerm.toLowerCase())
                      );
                    })
                    .map((option, j) => (
                      <Listbox.Option
                        key={option.value}
                        value={option.value}
                        className={({ active }) =>
                          cn('cursor-pointer px-3', {
                            'bg-green-50': active,
                            'rounded-b-lg':
                              i === optionGroups.length - 1 && j === group.options.length - 1,
                          })
                        }
                        data-testid={`dropdown-option-${option.value}`}
                      >
                        {({ selected }) => (
                          <Text
                            as="div"
                            className={cn('break-words py-3 text-volcanic-800', {
                              'font-medium': selected,
                              'border-b border-marble-500':
                                i !== optionGroups.length - 1 || j !== group.options.length - 1,
                            })}
                          >
                            {option.label ?? option.value}{' '}
                            {option.description && (
                              <Text as="span" className="text-volcanic-600">
                                ({option.description})
                              </Text>
                            )}
                          </Text>
                        )}
                      </Listbox.Option>
                    ))}
                </Fragment>
              ))}
            </Listbox.Options>
          </div>
        )}
      </Listbox>
      {description && (
        <Text as="span" styleAs="caption" className="mt-2 text-volcanic-700">
          {description}
        </Text>
      )}
    </div>
  );
};
