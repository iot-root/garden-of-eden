import { createEffect, createSignal } from "solid-js"

export const ErrorMessage = (props) => {
    const [isValidated, setValidated] = createSignal(false)

    createEffect((() => {
        setValidated(props.validator())
    }), [props])


    return (<div>
        {isValidated() ? "" : <p class="text-xs text-red-600">{props.message}</p>}
    </div>)
}