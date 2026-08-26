from django.core.management.base import BaseCommand

from entregas.models import Entrega


class Command(BaseCommand):
    """
    Comando opcional para ser agendado via cron no servidor de produção
    (ex.: uma vez por hora). O mesmo efeito já acontece automaticamente
    sempre que a API de entregas é consultada — este comando existe só
    como reforço, para quem preferir manter isso rodando periodicamente.
    """

    help = 'Marca como ATRASADA toda entrega pendente cuja data prevista já passou.'

    def handle(self, *args, **options):
        total = Entrega.objects.atualizar_atrasadas()
        self.stdout.write(
            self.style.SUCCESS(f'{total} entrega(s) marcada(s) como atrasada(s).')
        )
