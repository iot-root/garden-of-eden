import { Button } from '@/components/ui/button';
import { TextField, TextFieldRoot } from '@/components/ui/textfield';
import { addSchedule, deleteScheduleById, updateSchedule } from '@/endpoints/schedule';
import { formatTime } from '@/root/libs/parsers';
import { rangeValidator } from '@/root/libs/validators';
import { Checkbox } from '@/ui/checkbox/checkbox';
import { Match, Show, Switch, createEffect, createSignal } from 'solid-js';
import { Col } from '../containers/col';
import Padding from '../containers/padding';
import { Row } from '../containers/row';
import { Card } from '../ui/card';
import SensorToggle from '../ui/toggle/toggle';
import { ErrorMessage } from './error-message';

export const CreateSchedule = (props) => {
  const [job, setJob] = createSignal({})
  const [update, setUpdate] = createSignal(false)
  const [create, setCreate] = createSignal(false)

  // days
  const [sun, setSun] = createSignal(false);
  const [mon, setMon] = createSignal(false);
  const [tues, setTues] = createSignal(false);
  const [wed, setWed] = createSignal(false);
  const [thurs, setThurs] = createSignal(false);
  const [fri, setFri] = createSignal(false);
  const [sat, setSat] = createSignal(false);

  // time
  const [time, setTime] = createSignal("");

  // lights
  const [lightsRun, setLightsRun] = createSignal(false);
  const [lightsDuration, setLightsDuration] = createSignal(0);
  const [lightsBrightness, setLightsBrightness] = createSignal(0);

  // pump
  const [pumpRun, setPumpRun] = createSignal(false);
  const [pumpDuration, setPumpDuration] = createSignal(0);
  const [pumpSpeed, setPumpSpeed] = createSignal(0);

  // logs
  const [logSensors, setLogSensors] = createSignal("");

  createEffect(() => {
    if (props.create) {
      setCreate(props.create)
    }
    if (props.update) {
      setJob(props.job)
      setUpdate(props.update)
      setMon(job().day === 'Monday')
      setTues(job().day === 'Tuesday')
      setWed(job().day === 'Wednesday')
      setThurs(job().day === 'Thursday')
      setFri(job().day === 'Friday')
      setSat(job().day === 'Saturday')
      setSun(job().day === 'Sunday')
      setTime(formatTime(job().time))
      setLightsRun(String(job().details).split(' ')[0] === 'Brightness:')
      setLightsBrightness(String(job().details).split(' ')[1])
      setPumpRun(String(job().details).split(' ')[0] === 'Speed:')
      setPumpSpeed(String(job().details).split(' ')[1])
      setLogSensors(job().sensor === 'sensors')
    }
  })


  // form actions
  const onSubmit = async () => {
    const days = [sun(), mon(), tues(), wed(), thurs(), fri(), sat()];
    const countOfDays = days.filter((d) => d == true);
    if (countOfDays.length == 0) {
      console.error('Please select a day');
      return;
    }

    let timeString = time();
    if (!timeString) {
      console.error('Please select a time');
      return;
    }
    timeString = String(timeString).split(':');
    const mins = timeString[1];
    const hour = timeString[0];

    try {
      for (let i = 0; i < days.length; i++) {
        if (days[i]) {
          if (lightsRun()) {
            if (update()) {
              await updateSchedule('light', {
                id: job().id,
                minutes: Number(mins),
                hour: Number(hour),
                day: Number(i),
                state: 'on',
                brightness: Number(lightsBrightness()),
              });
            } else {
              await addSchedule('light', {
                minutes: Number(mins),
                hour: Number(hour),
                day: Number(i),
                state: 'on',
                brightness: Number(lightsBrightness()),
              });
            }

            // off
            const lightsDurationMins = Number(mins) + Number(lightsDuration());
            const remainder =
              lightsDurationMins < 60 ? 0 : lightsDurationMins % 60;

            if (update()) {
            } else {
              await addSchedule('light', {
                minutes:
                  remainder > 0
                    ? Number(remainder)
                    : Number(mins) + Number(lightsDuration()),
                hour: remainder > 0 ? Number(hour) + 1 : Number(hour),
                day: Number(i),
                state: 'off',
                brightness: 0,
              });
            }
          }

          if (pumpRun()) {
            if (update()) {
              // on
              await updateSchedule('pump', {
                id: job().id,
                minutes: Number(mins),
                hour: Number(hour),
                day: Number(i),
                state: 'on',
                speed: Number(pumpSpeed()),
              });
            } else {
              // on
              await addSchedule('pump', {
                minutes: Number(mins),
                hour: Number(hour),
                day: Number(i),
                state: 'on',
                speed: Number(pumpSpeed()),
              });
            }

            // off
            const pumpDurationMins = Number(mins) + Number(pumpDuration());
            const remainder = pumpDurationMins < 60 ? 0 : pumpDurationMins % 60;

            if (update()) {
            } else {
              await addSchedule('pump', {
                minutes: Number(remainder),
                hour: remainder > 0 ? Number(hour) + 1 : Number(hour),
                day: Number(i),
                state: 'off',
                speed: 0,
              });
            }
          }

          if (logSensors()) {
            if (update()) {
              await updateSchedule('log', {
                id: job().id,
                minutes: Number(mins),
                hour: Number(hour),
                day: Number(i),
                state: logSensors() ? 'on' : 'off',
              });
            } else {
              await addSchedule('log', {
                minutes: Number(mins),
                hour: Number(hour),
                day: Number(i),
              });
            }
          }
        }
      }
      await props.refetch().then(props.onClose());
    } catch (e) {
      console.error('Error creating schedule: ', e);
    }
  };

  const onCancel = () => {
    props.onClose();
  };

  const onDelete = async () => {
    await deleteScheduleById({ id: job().id });
    await props.refetch().then(props.onClose());
  };

  return (
    <Padding>
      <Card class="flex flex-col justify-start items-start w-[400px] max-h-[80vh] overflow-y-scroll">
        <div class="flex flex-col items-start mb-8">
          <p class="font-bold">Create Schedule</p>
          <p class="text-sm text-zinc-400">
            Change the details of this schedule.
          </p>
        </div>

        {/* Days */}
        <div class="flex flex-col items-start mb-8 w-full">
          <p class="font-medium mb-2">Days</p>
          <Section>
            <div class="flex flex-row justify-between w-[80%]">
              <div>
                <Checkbox label="Monday" checked={mon()} onChange={setMon} />
                <Checkbox label="Tuesday" checked={tues()} onChange={setTues} />
                <Checkbox label="Wednesday" checked={wed()} onChange={setWed} />
                <Checkbox
                  label="Thursday"
                  checked={thurs()}
                  onChange={setThurs}
                />
              </div>

              <div>
                <Checkbox label="Friday" checked={fri()} onChange={setFri} />
                <Checkbox label="Saturday" checked={sat()} onChange={setSat} />
                <Checkbox label="Sunday" checked={sun()} onChange={setSun} />
              </div>
            </div>
          </Section>
        </div>

        {/* Time */}
        <div class="flex flex-col items-start mb-8 w-full">
          <p class="font-medium mb-2">Time</p>
          <Section>
            <Row>
              <TextFieldRoot onChange={setTime} required class="w-full mr-2">
                <TextField type="time" value={time()} />
              </TextFieldRoot>
            </Row>
          </Section>
        </div>

        {/* Lights */}
        <div class="flex flex-col items-start mb-8 w-full">
          <Show when={!update() || (update() && lightsRun())}>
            <p class="font-medium mb-2">Lights</p>

            {/* run */}
            <Section class={`${create() ? "" : "hidden"}`}>
              <p class="text-sm leading-none text-zinc-400">Run</p>
              <SensorToggle
                checked={lightsRun()}
                onChange={() => setLightsRun(!lightsRun())}
              />
            </Section>

            {/* duration */}
            <Section class={`${create() ? "" : "hidden"}`}>
              <Col class="h-full">
                <p class="text-sm leading-none text-zinc-400">Duration</p>
                <ErrorMessage
                  validator={() => rangeValidator(lightsDuration(), 0, 59)}
                  message="Pick a value between 0 and 59."
                />
              </Col>
              <TextFieldRoot
                onChange={setLightsDuration}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(lightsDuration(), 0, 59) ? 'valid' : 'invalid'
                }
              >
                <TextField
                  type="number"
                  placeholder="mins"
                  value={lightsDuration()}
                />
              </TextFieldRoot>
            </Section>

            {/* brightness */}
            <Section>
              <Col class="h-full">
                <p class="text-sm leading-none text-zinc-400">Brightness %</p>
                <ErrorMessage
                  validator={() => rangeValidator(lightsBrightness(), 0, 100)}
                  message="Pick a value between 0 and 100."
                />
              </Col>
              <TextFieldRoot
                onChange={setLightsBrightness}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(lightsBrightness(), 0, 100) ? 'valid' : 'invalid'
                }
              >
                <TextField
                  type="number"
                  placeholder="%"
                  value={lightsBrightness()}
                />
              </TextFieldRoot>
            </Section>
          </Show>
        </div>

        {/* Pump */}
        <div class="flex flex-col items-start mb-8 w-full">
          <Show when={!update() || (update() && pumpRun())}>
            <p class="font-medium mb-2">Pump</p>

            <Section class={`${create() ? "" : "hidden"}`}>
              <Row class="w-full justify-between">
                <p class="text-sm leading-none text-zinc-400">Run</p>
                <SensorToggle
                  checked={pumpRun()}
                  onChange={() => setPumpRun(!pumpRun())}
                />
              </Row>
            </Section>

            <Section class={`${create() ? "" : "hidden"}`}>
              <Col class="h-full">
                <p class="text-sm leading-none text-zinc-400">Duration</p>
                <ErrorMessage
                  validator={() => rangeValidator(pumpDuration(), 0, 59)}
                  message="Pick a value between 0 and 59."
                />
              </Col>
              <TextFieldRoot
                onChange={setPumpDuration}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(lightsDuration(), 1, 59) ? 'valid' : 'invalid'
                }
              >
                <TextField
                  type="number"
                  placeholder="mins"
                  value={pumpDuration()}
                />
              </TextFieldRoot>
            </Section>

            <Section class={`${create() ? "" : "hidden"}`}>
              <Col class="h-full">
                <p class="text-sm leading-none text-zinc-400">Speed %</p>
                <ErrorMessage
                  validator={() => rangeValidator(pumpSpeed(), 0, 100)}
                  message="Pick a value between 0 and 100."
                />
              </Col>

              <TextFieldRoot
                onChange={setPumpSpeed}
                required
                class="w-16 mr-1"
                validationState={
                  rangeValidator(pumpDuration(), 0, 100) ? 'valid' : 'invalid'
                }
              >
                <TextField type="number" placeholder="%" value={pumpSpeed()} />
              </TextFieldRoot>
            </Section>
          </Show>
        </div>

        {/* Logs */}
        <div class="flex flex-col items-start mb-8 w-full">
          <Show when={!update() || (update() && logSensors())}>
            <p class="font-medium mb-2">Logs</p>
            <Section>
              {/* wrap in an array to ensure props.children.map works */}
              {[
                <Row class="w-full justify-between">
                  <p class="text-sm leading-none text-zinc-400">Sensors</p>
                  <SensorToggle
                    checked={logSensors()}
                    onChange={() => setLogSensors(!logSensors())}
                  />
                </Row>,
              ]}
            </Section>
          </Show>
        </div>

        {/* Buttons */}
        <div class="flex flex-row justify-between w-full">
          <Switch>
            <Match when={update()}>
              <Button variant="destructive" onClick={onDelete}>
                Delete
              </Button>
            </Match>
            <Match when={!update()}>
              <Button variant="destructive" onClick={onCancel}>
                Cancel
              </Button>
            </Match>
          </Switch>

          <Button onClick={onSubmit}>Save</Button>
        </div>
      </Card>
    </Padding>
  );
};

export const Section = (props) => {
  return (
    <Col class={`items-start w-full ${props.class}`}>
      <Row class={`justify-between w-full min-h-[40px]`}>{props.children}</Row>
    </Col>
  );
};
