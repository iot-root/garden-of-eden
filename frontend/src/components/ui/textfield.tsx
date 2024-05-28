import { cn } from '@/root/libs/cn';
import type { PolymorphicProps } from '@kobalte/core/polymorphic';
import * as TextFieldPrimitive from '@kobalte/core/text-field';
import { cva } from 'class-variance-authority';
import type { ValidComponent, VoidProps } from 'solid-js';
import { splitProps } from 'solid-js';

type TextFieldProps = TextFieldPrimitive.TextFieldRootProps & {
  class?: string
}

export const TextFieldRoot = <T extends ValidComponent = 'div'>(
  props: PolymorphicProps<T, TextFieldProps>
) => {
  const [local, rest] = splitProps(props as TextFieldProps, ['class']);

  return (
    <TextFieldPrimitive.Root class={cn('space-y-1', local.class)} {...rest} />
  );
};

const textfieldLabel = cva(
  'text-sm data-[disabled]:cursor-not-allowed data-[disabled]:opacity-70 font-medium',
  {
    variants: {
      label: {
        true: 'data-[invalid]:text-red-500 dark:data-[invalid]:text-red-900',
      },
      error: {
        true: 'text-red-500 dark:text-red-900',
      },
      description: {
        true: 'font-normal text-slate-500 dark:text-slate-400',
      },
    },
    defaultVariants: {
      label: true,
    },
  }
);

type TextFieldLabelProps = TextFieldPrimitive.TextFieldLabelProps & {
  class?: string
}

export const TextFieldLabel = <T extends ValidComponent = 'label'>(
  props: PolymorphicProps<T, TextFieldLabelProps>
) => {
  const [local, rest] = splitProps(props as TextFieldLabelProps, ['class']);

  return (
    <TextFieldPrimitive.Label
      class={cn(textfieldLabel(), local.class)}
      {...rest}
    />
  );
};

type TextFieldErrorMessageProps =
  TextFieldPrimitive.TextFieldErrorMessageProps & {
    class?: string
  }

export const TextFieldErrorMessage = <T extends ValidComponent = 'div'>(
  props: PolymorphicProps<T, TextFieldErrorMessageProps>
) => {
  const [local, rest] = splitProps(props as TextFieldErrorMessageProps, [
    'class',
  ]);

  return (
    <TextFieldPrimitive.ErrorMessage
      class={cn(textfieldLabel({ error: true }), local.class)}
      {...rest}
    />
  );
};

type TextFieldDescriptionProps =
  TextFieldPrimitive.TextFieldDescriptionProps & {
    class?: string
  }

export const TextFieldDescription = <T extends ValidComponent = 'div'>(
  props: PolymorphicProps<T, TextFieldDescriptionProps>
) => {
  const [local, rest] = splitProps(props as TextFieldDescriptionProps, [
    'class',
  ]);

  return (
    <TextFieldPrimitive.Description
      class={cn(textfieldLabel({ description: true }), local.class)}
      {...rest}
    />
  );
};

type TextFieldInputProps = VoidProps<
  TextFieldPrimitive.TextFieldInputProps & {
    class?: string
  }
>

export const TextField = <T extends ValidComponent = 'input'>(
  props: PolymorphicProps<T, TextFieldInputProps>
) => {
  const [local, rest] = splitProps(props as TextFieldInputProps, ['class']);

  return (
    <TextFieldPrimitive.Input
      class={cn(
        'flex h-9 w-full rounded-md border border-slate-200bg-transparent px-3 py-1 text-sm shadow-sm transition-shadow file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-[1.5px] focus-visible:ring-slate-950 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:placeholder:text-slate-400 dark:focus-visible:ring-slate-300',
        local.class
      )}
      {...rest}
    />
  );
};
