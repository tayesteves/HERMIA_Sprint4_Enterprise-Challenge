**Tabela FUNCIONARIO**:
   - **Chave Primária**: `ID_FUNCIONARIO` (gerada por IDENTITY) garante unicidade e serve como identificador único
   - **Restrições**:
       - `NOT NULL` em todas as colunas previne dados ausentes
       - `CHECK (Salario >= 1518)` evita salários abaixo do mínimo.
**Tabela LEITURA_SENSORES**:
   - **Chave Primária**: `ID_LEITURA_SENSORES` (IDENTITY) identifica cada leitura exclusivamente.
   - **Chave Estrangeira**: `ID_MAQUINA` (FK_LEITURA_MAQUINA) vincula a tabela a MAQUINA_AUTONOMA, mantendo integridade referencial.
   - **Restrições**:
       - `NOT NULL` em várias colunas previne dados ausentes.
       - `CHECK` define intervalos (ex.: TEMPERATURA -50 a 150, UMIDADE 0 a 100, FALHA 0 ou 1, LUMINOSIDADE 0 a 1000, VIBRACAO 0 a 100, QUALIDADE_AR 0 a 500, DIAS_ULTIMA_MANUTENCAO 0 a 37000) para validação de dados sensoriais.
**Tabela MANUTENCAO**:
   - **Chave Primária**: `ID_MANUTENCAO` (IDENTITY) assegura unicidade.
   - **Chaves Estrangeiras**:
	   - `ID_FUNCIONARIO` (FK_MANUTENCAO_FUNCIONARIO) liga a FUNCIONARIO.
       - `ID_MAQUINA` (FK_MANUTENCAO_MAQUINA) liga a MAQUINA_AUTONOMA, garantindo consistência.
   - **Restrições**: `NOT NULL` em todas as colunas previne dados ausentes.
**Tabela MAQUINA_AUTONOMA**:
   - **Chave Primária**: `ID_MAQUINA` (IDENTITY) assegura unicidade.
   - **Restrições**:
       - `NOT NULL` em várias colunas evita dados incompletos
       - `CHECK (Tipo IN ('Solda', 'Corte', 'Montagem', 'Pintura'))` limita os tipos válidos.