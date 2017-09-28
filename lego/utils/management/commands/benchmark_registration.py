import cProfile
from datetime import timedelta

from django.utils import timezone

from lego.apps.events import constants
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tasks import async_register
from lego.apps.users.models import AbakusGroup, User
from lego.utils.management_command import BaseCommand


class Command(BaseCommand):
    help = 'Benchmark registration methods'

    def add_arguments(self, parser):
        parser.add_argument(
            '--single',
            action='store_true',
            default=False,
            help='Single registration benchmark',
        )

        parser.add_argument(
            '--singleavg',
            action='store_true',
            default=False,
            help='Single registration benchmark average',
        )
        parser.add_argument(
            '--multi',
            action='store_true',
            default=False,
            help='200 registration benchmark',
        )

    def run(self, *args, **options):

        user_group = AbakusGroup.objects.get_or_create(name='Users')[0]
        abakus_group = AbakusGroup.objects.get_or_create(name='Abakus')[0]
        users = []

        for i in range(200):
            first_name = last_name = username = email = str(i)
            user = User.objects.get_or_create(
                username=username, first_name=first_name, last_name=last_name, email=email
            )[0]
            user_group.add_user(user)
            users.append(user)

        event = Event.objects.create(
            title="Test", start_time=(timezone.now() + timedelta(days=1)),
            end_time=(timezone.now() + timedelta(days=1)),
            location="-", event_type=constants.COMPANY_PRESENTATION
        )
        event.title = f'{event.id}'
        event.save()
        pool1 = Pool.objects.create(
            event=event, name="Users", capacity=100,
            activation_date=(timezone.now() - timedelta(days=1))
        )
        pool1.permission_groups.set([user_group.id])
        pool2 = Pool.objects.create(
            event=event, name="Abakus", capacity=10,
            activation_date=(timezone.now() - timedelta(days=1))
        )
        pool2.permission_groups.set([abakus_group.id])

        def single_benchmark(event, user):

            reg = Registration.objects.get_or_create(event=event, user=user)[0]

            pr = cProfile.Profile()
            pr.enable()

            reg.event.register(reg)
            pr.disable()
            pr.dump_stats(f'single{event.id}.pstat')

        def single_benchmark_avg(event, users):

            regs = []
            for user in users:
                reg = Registration.objects.get_or_create(event=event, user=user)[0]
                regs.append(reg)

            pr = cProfile.Profile()
            pr.enable()
            for reg in regs:
                reg.event.register(reg)
            pr.disable()
            pr.dump_stats(f'single_avg{event.id}.pstat')

        def benchmark(event, users):

            regs = []
            for user in users:
                reg = Registration.objects.get_or_create(event=event, user=user)[0]
                regs.append(reg)
            time = timezone.now() + timedelta(seconds=5)
            for reg in regs:
                async_register.apply_async((reg.id,), eta=time)

            input('Start the celery workers: DONE?')

            registrations = Registration.objects.filter(event=event).order_by('registration_date')

            first = registrations.first()
            last = registrations.last()

            diff = last.registration_date - first.registration_date
            print(f'Number of registrations: {registrations.count()}')
            print(f'Number pool1 {pool1.registrations.count()} / 100')
            print(f'Number pool2 {pool2.registrations.count()} / 10')
            print(f'Time per registration {diff.total_seconds() * 1000 / registrations.count()}')
            print(f'Total time: {diff.total_seconds() * 1000}')

        if options['single']:
            single_benchmark(event, users[0])
        elif options['singleavg']:
            single_benchmark_avg(event, users)
        elif options['multi']:
            benchmark(event, users)
