import { cn } from '@/root/libs/cn';
import * as CheckboxPrimitive from '@kobalte/core/checkbox';
import type { PolymorphicProps } from '@kobalte/core/polymorphic';
import { splitProps, type ValidComponent, type VoidProps } from 'solid-js';

export const CheckboxLabel = CheckboxPrimitive.Label;
export const Checkbox = CheckboxPrimitive.Root;
export const CheckboxErrorMessage = CheckboxPrimitive.ErrorMessage;
export const CheckboxDescription = CheckboxPrimitive.Description;

type CheckboxControlProps = VoidProps<
  CheckboxPrimitive.CheckboxControlProps & { class?: string }
>

export const CheckboxControl = <T extends ValidComponent = 'div'>(
  props: PolymorphicProps<T, CheckboxControlProps>
) => {
  const [local, rest] = splitProps(props as CheckboxControlProps, [
    'class',
    'children',
  ]);

  return (
    <>
      <CheckboxPrimitive.Input class="[&:focus-visible+div]:outline-none [&:focus-visible+div]:ring-[1.5px] [&:focus-visible+div]:ring-slate-950 [&:focus-visible+div]:ring-offset-2 [&:focus-visible+div]:ring-offset-white dark:[&:focus-visible+div]:ring-slate-300 dark:[&:focus-visible+div]:ring-offset-slate-950" />
      <CheckboxPrimitive.Control
        class={cn(
          'h-4 w-4 shrink-0 rounded-sm border border-slate-200 shadow transition-shadow focus-visible:outline-none focus-visible:ring-[1.5px] focus-visible:ring-slate-950 data-[disabled]:cursor-not-allowed data-[checked]:bg-slate-900 data-[checked]:text-slate-50 data-[disabled]:opacity-50 dark:border-slate-800 dark:border-slate-50 dark:focus-visible:ring-slate-300 dark:data-[checked]:bg-slate-50 dark:data-[checked]:text-slate-900',
          local.class
        )}
        {...rest}
      >
        <CheckboxPrimitive.Indicator class="flex items-center justify-center text-current">

        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Control>
    </>
  );
};
