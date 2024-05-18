export const H1 = (props) => {
  return (
    <h1 class={`text-left scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl mb-1 ${props.class}`}>
      {props.children}
    </h1>
  );
};


export const H2 = (props) => {
  return (
    <h2 class="text-left scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight transition-colors first:mt-0">
      {props.children}
    </h2>
  );
};


export const H3 = (props) => {
  return <h3 class={`text-left scroll-m-20 text-2xl font-semibold tracking-tight ${props.class}`}>{props.children}</h3>;
};


export const H4 = (props) => {
  return (
    <h4 class="text-left scroll-m-20 text-xl font-semibold tracking-tight">{props.children}</h4>
  );
};


export const P = (props) => {
  return (
    <p class={`text-left not-first:mt-6 leading-7 ${props.class}`}>
      {props.children}
    </p>
  );
};


export const Detail = (props) => {
  return (
    <p class={`text-xs text-left  ${props.class} ${props.isFailed ? "text-red-600" : "text-zinc-400"}`}>
      {props.children}
    </p>
  );
};

