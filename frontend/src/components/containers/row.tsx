export const Row = (props) => {
  return (
    <div class={`flex flex-row justify-start items-center ${props.class}`}>
      {props.children}
    </div>
  );
};
