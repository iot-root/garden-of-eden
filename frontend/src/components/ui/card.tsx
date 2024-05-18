export const Card = (props) => {
    return (
        <div class={`border bg-white w-full p-4 ${props.class}`}>{props.children}</div>
    )
}