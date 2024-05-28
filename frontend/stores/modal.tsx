import { createStore } from "solid-js/store";

export const [modalStore, setModalStore] = createStore({
    display: false,
    content: null
});

export const toggleModal = (v) => {
    setModalStore("display", v);
};

export const setModalContent = (content) => {
    setModalStore("content", content);
};