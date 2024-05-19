export const Center = (props) => {
    return (
        <div class={`flex flex-col justify-center items-center ${props.class}`}>{props.children}</div>
    )
}