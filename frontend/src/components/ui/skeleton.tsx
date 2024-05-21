import { cn } from "@/libs/cn";
import { splitProps, type ComponentProps } from "solid-js";

export const Skeleton = (props: ComponentProps<"div">) => {
  const [local, rest] = splitProps(props, ["class"]);

  return <div class={cn("animate-pulse rounded-md bg-gray-300 dark:bg-gray-400", local.class)} {...rest} />;
};
