import styles from './Button.module.css';


export const Button: any = (props: { text: string, cb: () => {} }) => {
    return (
        <button class={styles.Button}  onClick={() => props.cb()}>
            {props.text}
        </button>
    )
}