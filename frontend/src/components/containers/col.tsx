export const Col = (props) => {
  return (
    <div class={`flex flex-col justify-start items-start ${props.class}`}>
      {props.children}
    </div>
  );
};
