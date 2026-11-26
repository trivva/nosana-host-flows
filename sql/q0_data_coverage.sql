-- Q0: first and last NOS transfer available in the CDP dataset (how far back can we go?)
SELECT
  MIN(block_time) AS first_transfer,
  MAX(block_time) AS last_transfer,
  COUNT(*)        AS n_transfers
FROM solana.transfers
WHERE mint = 'nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7'
