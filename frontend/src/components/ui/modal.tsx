import { modalStore, toggleModal } from "@/root/stores/modal";
import { createEffect, onCleanup } from "solid-js";


export const Modal = () => {
    createEffect(() => {
        console.log(modalStore.content)
    }, [modalStore])

    let modalRef

    const handleOutsideClick = (evt) => {
        if (modalRef && !modalRef.contains(evt.target)) {
            toggleModal(false)
        }
    }

    document.addEventListener('click', handleOutsideClick, true);

    onCleanup(() => {
        document.removeEventListener('click', handleOutsideClick, true);
    });

    return (<>
        {
            modalStore.display &&
            (<div class="fixed top-0 left-0 flex flex-col justify-center items-center w-[100vw] h-[100vh] bg-black/5">
                {/* Blurred background */}
                <div class="z-100 fixed w-[100vw] h-[100vh] backdrop-blur-sm"></div>

                {/* Modal content, unblurred */}
                <div ref={modalRef} class="relative top-0 z-10">
                    {modalStore.content}
                </div>
            </div>)
        }
    </>)
}