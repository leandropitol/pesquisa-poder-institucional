# Extrai do vdem.RData (pacote oficial vdemdata) as variáveis usadas pelo protocolo e grava CSV
# em data/staging/vdem/. Não altera valores: só seleciona colunas e anos.
#
# Uso: Rscript src/normalizacao/vdem_extrair.R <arquivo.RData> <saida.csv> <ano_inicial>

args <- commandArgs(trailingOnly = TRUE)
entrada <- args[1]
saida <- args[2]
ano_inicial <- as.integer(args[3])

e <- new.env()
nome <- load(entrada, envir = e)[1]
v <- e[[nome]]
colunas <- c("country_text_id", "country_name", "year", "v2x_regime", "v2x_libdem")
sel <- v[v$year >= ano_inicial, colunas]
dir.create(dirname(saida), recursive = TRUE, showWarnings = FALSE)
write.csv(sel, saida, row.names = FALSE, fileEncoding = "UTF-8", na = "")
cat(sprintf("%d linhas, %d países, anos %d a %d\n", nrow(sel), length(unique(sel$country_text_id)), min(sel$year), max(sel$year)))
