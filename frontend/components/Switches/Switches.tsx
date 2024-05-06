import styles from './Switches.module.css';

export const Switches = (props) => {
    return (
        <div class={styles.Panel}>
            <h2>{props.title}</h2>
            <div class={styles.Switches}>
                {props.children}
            </div>
        </div>
    )
}