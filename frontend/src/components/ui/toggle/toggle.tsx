import { Switch, SwitchControl, SwitchThumb } from "@/components/ui/toggle/switch";

const SensorToggle = (props) => {
    return (
        <Switch class="flex items-center space-x-2" checked={props.checked} onChange={props.onChange}>
            <SwitchControl>
                <SwitchThumb />
            </SwitchControl>
        </Switch>
    );
};

export default SensorToggle;