import {
  Checkbox as CheckboxComp,
  CheckboxControl,
  CheckboxLabel,
} from './checkbox-control';

export const Checkbox = (props) => {
  return (
    <CheckboxComp
      class="flex items-start space-x-0 mb-2"
      checked={props.checked}
      onChange={props.onChange}
    >
      <div class="mr-2">
        <CheckboxControl />
      </div>
      <div class="grid gap-1.5 leading-none">
        <CheckboxLabel class="text-sm leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {props.label}
        </CheckboxLabel>
      </div>
    </CheckboxComp>
  );
};
