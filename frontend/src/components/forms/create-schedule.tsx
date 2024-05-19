import { Button } from "@/components/ui/button";
import { TextField, TextFieldRoot } from "@/components/ui/textfield";
import { Checkbox } from "@/ui/checkbox/checkbox";
import { rangeValidator } from "@/validators/range";
import { createSignal } from "solid-js";
import { Col } from "../containers/col";
import Padding from "../containers/padding";
import { Row } from "../containers/row";
import { Card } from "../ui/card";
import SensorToggle from "../ui/toggle/toggle";
import { ErrorMessage } from "./error-message";

export const CreateSchedule = () => {
    // days
    const [sun, setSun] = createSignal(false)
    const [mon, setMon] = createSignal(false)
    const [tues, setTues] = createSignal(false)
    const [wed, setWed] = createSignal(false)
    const [thurs, setThurs] = createSignal(false)
    const [fri, setFri] = createSignal(false)
    const [sat, setSat] = createSignal(false)

    // time
    const [time, setTime] = createSignal()

    // lights
    const [lightsRun, setLightsRun] = createSignal(false)
    const [lightsDuration, setLightsDuration] = createSignal(0)
    const [lightsBrightness, setLightsBrightness] = createSignal(0)

    // pump
    const [pumpRun, setPumpRun] = createSignal(false)
    const [pumpDuration, setPumpDuration] = createSignal(0)
    const [pumpSpeed, setPumpSpeed] = createSignal(0)

    // logs
    const [logTemp, setLogTemp] = createSignal(false)
    const [logHumidity, setLogHumidity] = createSignal(false)
    const [logPCBTemp, setLogPCBTemp] = createSignal(false)
    const [logCameras, setLogCameras] = createSignal(false)

    // form actions
    const onSubmit = () => {
        // convert to valid form component, check required fields, validate and reject
        console.log("submitting")
    }

    return (
        <Padding>
            <Card class="flex flex-col justify-start items-start">
                <div class="flex flex-col items-start mb-8">
                    <p class="font-bold">Create Schedule</p>
                    <p class="text-sm text-zinc-400">Change the details of this schedule.</p>
                </div>

                {/* days */}
                <Section title="Days">
                    {[<div class="flex flex-row justify-between w-[80%]">
                        <div>
                            <Checkbox label="Monday" check={mon()} onChange={() => setMon(!mon())} />
                            <Checkbox label="Tuesday" check={tues()} onChange={() => setTues(!tues())} />
                            <Checkbox label="Wednesday" check={wed()} onChange={() => setWed(!wed())} />
                            <Checkbox label="Thursday" check={thurs()} onChange={() => setThurs(!thurs())} />
                        </div>

                        <div>
                            <Checkbox label="Friday" check={fri()} onChange={() => setFri(!fri())} />
                            <Checkbox label="Saturday" check={sat()} onChange={() => setSat(!sat())} />
                            <Checkbox label="Sunday" check={sun()} onChange={() => setSun(!sun())} />
                        </div>
                    </div>]}
                </Section>

                {/* time */}
                <Section title="Time">
                    {[<Row>
                        <TextFieldRoot onChange={setTime} required class="w-full mr-2" >
                            <TextField type="time"
                            />
                        </TextFieldRoot>
                    </Row>]}
                </Section>

                {/* Lights */}
                <Section title="Lights">
                    <>
                        <p class="font-light">Run</p>
                        <SensorToggle checked={lightsRun()} onChange={() => setLightsRun(!lightsRun())} />
                    </>

                    <>
                        <Col class="h-full">
                            <p class="font-light">Duration</p>
                            <ErrorMessage validator={() => rangeValidator(lightsDuration(), 0, 59)} message="Pick a value between 0 and 59." />
                        </Col>
                        <TextFieldRoot onChange={setLightsDuration} required class="w-16 mr-1" validationState={rangeValidator(lightsDuration(), 1, 59) ? "valid" : "invalid"}>
                            <TextField type="number" placeholder="mins"
                                value={lightsDuration()} />
                        </TextFieldRoot>
                    </>

                    <>
                        <Col class="h-full">
                            <p class="font-light">Brightness</p>
                            <ErrorMessage validator={() => rangeValidator(lightsBrightness(), 0, 100)} message="Pick a value between 0 and 100." />
                        </Col>
                        <TextFieldRoot onChange={setLightsBrightness} required class="w-16 mr-1" validationState={rangeValidator(lightsBrightness(), 0, 100) ? "valid" : "invalid"}>
                            <TextField type="number" placeholder="%"
                                value={lightsBrightness()} />
                        </TextFieldRoot>
                    </>
                </Section>

                {/* Pump */}
                <Section title="Pump">
                    <>
                        <Row class="w-full justify-between">
                            <p class="font-light">Run</p>
                            <SensorToggle checked={pumpRun()} onChange={() => setPumpRun(!pumpRun())} />
                        </Row>
                    </>
                    <>
                        <Col class="h-full">
                            <p class="font-light">Duration</p>
                            <ErrorMessage validator={() => rangeValidator(pumpDuration(), 0, 59)} message="Pick a value between 0 and 59." />
                        </Col>
                        <TextFieldRoot onChange={setPumpDuration} required class="w-16 mr-1" validationState={rangeValidator(lightsDuration(), 1, 59) ? "valid" : "invalid"}>
                            <TextField type="number" placeholder="mins"
                                value={pumpDuration()} />
                        </TextFieldRoot>
                    </>

                    <>
                        <Col class="h-full">
                            <p class="font-light">Speed</p>
                            <ErrorMessage validator={() => rangeValidator(pumpSpeed(), 0, 100)} message="Pick a value between 0 and 100." />
                        </Col>

                        <TextFieldRoot onChange={setPumpSpeed} required class="w-16 mr-1" validationState={rangeValidator(pumpDuration(), 0, 100) ? "valid" : "invalid"}>
                            <TextField type="number" placeholder="%"
                                value={pumpSpeed()} />
                        </TextFieldRoot>
                    </>
                </Section>

                {/* Logs */}
                <Section title="Logs">
                    <Row class="w-full justify-between">
                        <p class="font-light">Temp</p>
                        <SensorToggle check={logTemp()} onChange={() => setLogTemp(!logTemp())} />
                    </Row>

                    <Row class="w-full justify-between">
                        <p class="font-light">Humidity</p>
                        <SensorToggle check={logHumidity()} onChange={() => setLogHumidity(!logHumidity())} />
                    </Row>

                    <Row class="w-full justify-between">
                        <p class="font-light">PCB Temp</p>
                        <SensorToggle check={logPCBTemp()} onChange={() => setLogPCBTemp(!logPCBTemp())} />
                    </Row>

                    <Row class="w-full justify-between">
                        <p class="font-light">Cameras</p>
                        <SensorToggle check={logCameras()} onChange={() => setLogCameras(!logCameras())} />
                    </Row>
                </Section>

                {/* Buttons */}
                <div class="flex flex-row justify-between w-full">
                    <Button variant="destructive">Delete</Button>
                    <Button onClick={onSubmit}>Save</Button>
                </div>
            </Card>
        </Padding >
    )
}

export const Section = (props) => {
    return (
        <Col class="mb-8 items-start w-full">
            <p class="font-medium mb-2">{props.title}</p>
            <Col class="w-full">
                {
                    props.children.map((child) => {
                        return (
                            <Row class="justify-between w-full min-h-[40px]">
                                {child}
                            </Row>
                        )
                    })
                }
            </Col>
        </Col>
    )
}