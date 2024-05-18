import { Add as AddIcon } from "@/icons/icons"


export const Add = (props) => {
    return (
        <div class="flex flex-row justify-end items-center">
            <p class="mr-4 text-zinc-400 font-light" >{props.label}</p>
            <AddIcon height={40} width={40} />
        </div>
    )
}