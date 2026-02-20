# FLEXT Tap LDAP

Singer Tap para extracao de dados de diretorios LDAP em pipelines de integracao.

Descricao oficial atual: "FLEXT Tap LDAP - Singer Tap for LDAP Directory Services".

## O que este projeto entrega

- Extrai registros LDAP e emite eventos Singer.
- Padroniza schema para ingestao downstream.
- Apoia sincronizacao de dados de identidade.

## Contexto operacional

- Entrada: origem LDAP configurada.
- Saida: stream Singer de registros e catalogo.
- Dependencias: flext-ldap e orquestracao Meltano/Singer.

## Estado atual e risco de adocao

- Qualidade: **Alpha**
- Uso recomendado: **Nao produtivo**
- Nivel de estabilidade: em maturacao funcional e tecnica, sujeito a mudancas de contrato sem garantia de retrocompatibilidade.

## Diretriz para uso nesta fase

Aplicar este projeto somente em desenvolvimento, prova de conceito e homologacao controlada, com expectativa de ajustes frequentes ate maturidade de release.
