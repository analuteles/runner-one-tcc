from rest_framework import serializers

from .models import Ferias


class FeriasSerializer(serializers.ModelSerializer):
    motorista_nome = serializers.CharField(source='motorista.nome', read_only=True)
    situacao = serializers.CharField(read_only=True)

    class Meta:
        model = Ferias
        fields = [
            'id',
            'motorista',
            'motorista_nome',
            'data_inicio',
            'data_fim',
            'situacao',
            'observacao',
            'data_cadastro',
        ]
        read_only_fields = ['id', 'data_cadastro']

    def validate(self, attrs):
        motorista = attrs.get('motorista', getattr(self.instance, 'motorista', None))
        data_inicio = attrs.get('data_inicio', getattr(self.instance, 'data_inicio', None))
        data_fim = attrs.get('data_fim', getattr(self.instance, 'data_fim', None))

        if data_inicio and data_fim and data_fim < data_inicio:
            raise serializers.ValidationError(
                {'data_fim': 'A data de término não pode ser anterior à data de início.'}
            )

        if motorista and data_inicio and data_fim:
            conflitos = Ferias.objects.filter(
                motorista=motorista, data_inicio__lte=data_fim, data_fim__gte=data_inicio
            )
            if self.instance:
                conflitos = conflitos.exclude(pk=self.instance.pk)
            if conflitos.exists():
                raise serializers.ValidationError(
                    'Este motorista já possui férias registradas nesse período.'
                )

        return attrs
