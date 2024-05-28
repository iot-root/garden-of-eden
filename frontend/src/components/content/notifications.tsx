import { For } from 'solid-js';
import Padding from '@/components/containers/padding';
import { Caution, Notice, Warning } from '@/icons/icons';
import data from '@/root/data.json';
import { H1, P } from '@/typography/heading';
import { Card } from '@/ui/card';
import { Notification } from '@/ui/notification';

export const Notifications = () => {
  return (
    <Padding>
      <H1 class="mb-4">Notifications</H1>
      <For each={Object.entries(data.notifications)}>
        {(n) => {
          return (
            <Card class="p-[8px] mb-2">
              <Notification>
                <div class="flex flex-row justify-between items-center">
                  <P>{n[1].message}</P>
                  {n[1].severity === 'low' ? <Notice /> : ''}
                  {n[1].severity === 'mid' ? <Caution /> : ''}
                  {n[1].severity === 'high' ? <Warning /> : ''}
                </div>
              </Notification>
            </Card>
          );
        }}
      </For>
    </Padding>
  );
};
