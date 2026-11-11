-- Export B: NOS sent per host per day, by destination category
WITH deployers AS (
  SELECT DISTINCT source_owner AS addr
  FROM solana.transfers
  WHERE mint = 'nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7'
    AND destination_owner IN (
    '9gtjTgK9XP5dPNhriQQceqR1J6uZVqbXt9sR5xqec5zR',
    'vyvosAzz8i3nJCgM723pQVFmpfP5juDixBTmRzDUXCz',
    'DNRPP8a8m9dZ6buyEoFH4BFn8psaccSqeEMVCiRLM8L7',
    'C5EVJ6KfVMwWK3Go52nJhNAbhskC21u1Srpbak2HPQVy',
    '5rbzHcGwCqF4kK31fp67RHKbt3GxTRhTxuvFoELgSace',
    'Dqx5MbcAGQo2vgWaUau81joSJwDTaMzdRt1CEX8xzxUj',
    '3X6dBiFS6L34tC39uph85KpM9LxWourbgYEGVRvfvcNz',
    'A365x5mvyvaxFyZVKPb56NeekiTThhzfGyY3YUSTnZs7',
    'FXD689FKMNm4pwLrrjmauu8YqJB7qQ54ZXa5eBrG4ERc',
    'EbPRR7md4WPRtqNHjTvfTxaMniFPsrQro37trKTPC37s',
    '4wztCaN3VFp7DsAiaTanBfALPRAnGtweGhd3JuoqJSBw',
    '5acCMyZNoxyFjU7RMSF4bicT5m3DVqY5p8BJFeBGUhqB',
    'EYZESGGY1rn2mEqMkzokKP4fxHcFePqhgwxp3ruacU5V',
    '88u851QxSRaCwCgned9AASDwEhCUP5iitLBRapxFg7Dg',
    '5AgKD7XFDubFQdgniCLjCTnZ6wAmHzdWtVGtV1CbHv4g',
    'FwyQAkvJNVhmh2RW2cWn9CFWp1SpuCq6bMckEk9RLUwq',
    'Hxy5Pxy57PrYYK2mp4FfA5VCUcfXEucU3ivSkSC1Q64Q',
    '75mB6NGPPM3n1WLrozc2Q1n2hJ1e7W33ttjFrLfc46kn',
    '6M5REuhLJatxxCdWD6ZfeLC7wyncSUAC9Q5sSKxTUJsK',
    '55gVTCYfxTMvB2dxSMHAYLgtN91ydKVFLQHuTfuf8WT3',
    'FuNLsoaJg1c2PjJqWXMKJSuL6aWKXGs7nHMN7QZUNZvc',
    'hnxMznEg6AZjDTQ5doFs1AYp7QrBPEWeHVYQpL3SAaW',
    'DmRVspk6LMLyG5UCNThCBoQBo9QKRqHJBT7Sjof6i1j9',
    'HQve6GMgn1XZeQCDKdCTm3D7KtHWmjzhqkTnVedr1NG3',
    'BAsAbV6kzhczKaVUzbbDt11ir6QYDkHTJ7bgUxVdpSoJ',
    '76yS3U99Ejb6swgBwPxhkrQcH2jbMTN4KZjCR27S64mt',
    'E1bmuXsDYbAWXyF7jD1w3aAagJZWmfFnp44hz46sj1eY',
    'KvS8AdzYd24ufE9RoXC5hSG1TBMYgeQwNAR9AjYnHMS',
    'DJfGpWbxbWyYfjgDbDvmBXrUDC2JMV5xyKJPErj1hNv4',
    'HH4n6hDkak1wobC8MfRfFPiaLvBEn24cDmUtKejNX5Ey',
    'DkaiMZe1V829xUEKB8LYwm3RBNqZbU8ARF1ddURZnrZg',
    'GxdMZoXVdWeXcZJsNpQbBbURzMKLhWmqHXXNthyFnukp',
    'Anksv5GGAdD4XsbuSDJYZEK8unRPAY14uyqtcXmssNAV',
    '4d52aY94ctK8wqVejNNfXuY6zbNLHWT1VdKmXuV2XscD',
    'HTsZs7zrSMPxuq9oKyW1m5NZcQt22rbQrXscE7j4fxJK',
    'giLkCXycxMP9u2Z6jBQ7Hr4E7ui7WS49gDka1Yvqymn',
    'CgQXt5hVJMF5sd2XijVknbhsWzsbByyYLBeKyj1VTEpw',
    '55X5BunVafshC8AjzpRUCKMy9k4Z8ZGjfbsjjtXQzxrL',
    'HtKPdEwHfsu2pEQ6TADKeKpiENvfEkrnSmFDcxcSCn6m',
    'FjsPx5cRBxLUxpi86SwaCsi2j2dswUVth1Y3uLzEmbG8',
    'E5YT9wgyPUtFrfmM6jTjUmpZxWCN4HWBf7nZi5p2qJbK',
    '36uhrwu8bRgzVQGFJs9UbebppyHRrWwx6m49BdsgApvD',
    'FwuCDc4BUpmsTNCWbvvZA7gYZr5ow1N4X4d6RdyAP8UT',
    '6B1zVzMqZvjEWT5HyJg83WTwQLF7j8wdbDGkCeRs5FRv',
    '3TEpufUCvs2bGbnfwe6xWtA7UxPDo8D3iVj6Be5rgeVF',
    'CJYLwZQXkSaawsdfYtSWs2LAvR2dp91VRsm7UcrkZmb8',
    '4KF3XCeSLEHC1AZNjXy5ap47oKLr6aecGuLmmo75859N',
    '4CRJ95N49P1Kzp3TizRA54GgRkLPzyQVb7j3MkWtVTv7'
    )
),
hosts AS (
  SELECT DISTINCT t.destination_owner AS host
  FROM solana.transfers AS t
  LEFT JOIN deployers AS d ON t.destination_owner = d.addr
  WHERE t.mint = 'nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7'
    AND t.source_owner IN (
    '9gtjTgK9XP5dPNhriQQceqR1J6uZVqbXt9sR5xqec5zR',
    'vyvosAzz8i3nJCgM723pQVFmpfP5juDixBTmRzDUXCz',
    'DNRPP8a8m9dZ6buyEoFH4BFn8psaccSqeEMVCiRLM8L7',
    'C5EVJ6KfVMwWK3Go52nJhNAbhskC21u1Srpbak2HPQVy',
    '5rbzHcGwCqF4kK31fp67RHKbt3GxTRhTxuvFoELgSace',
    'Dqx5MbcAGQo2vgWaUau81joSJwDTaMzdRt1CEX8xzxUj',
    '3X6dBiFS6L34tC39uph85KpM9LxWourbgYEGVRvfvcNz',
    'A365x5mvyvaxFyZVKPb56NeekiTThhzfGyY3YUSTnZs7',
    'FXD689FKMNm4pwLrrjmauu8YqJB7qQ54ZXa5eBrG4ERc',
    'EbPRR7md4WPRtqNHjTvfTxaMniFPsrQro37trKTPC37s',
    '4wztCaN3VFp7DsAiaTanBfALPRAnGtweGhd3JuoqJSBw',
    '5acCMyZNoxyFjU7RMSF4bicT5m3DVqY5p8BJFeBGUhqB',
    'EYZESGGY1rn2mEqMkzokKP4fxHcFePqhgwxp3ruacU5V',
    '88u851QxSRaCwCgned9AASDwEhCUP5iitLBRapxFg7Dg',
    '5AgKD7XFDubFQdgniCLjCTnZ6wAmHzdWtVGtV1CbHv4g',
    'FwyQAkvJNVhmh2RW2cWn9CFWp1SpuCq6bMckEk9RLUwq',
    'Hxy5Pxy57PrYYK2mp4FfA5VCUcfXEucU3ivSkSC1Q64Q',
    '75mB6NGPPM3n1WLrozc2Q1n2hJ1e7W33ttjFrLfc46kn',
    '6M5REuhLJatxxCdWD6ZfeLC7wyncSUAC9Q5sSKxTUJsK',
    '55gVTCYfxTMvB2dxSMHAYLgtN91ydKVFLQHuTfuf8WT3',
    'FuNLsoaJg1c2PjJqWXMKJSuL6aWKXGs7nHMN7QZUNZvc',
    'hnxMznEg6AZjDTQ5doFs1AYp7QrBPEWeHVYQpL3SAaW',
    'DmRVspk6LMLyG5UCNThCBoQBo9QKRqHJBT7Sjof6i1j9',
    'HQve6GMgn1XZeQCDKdCTm3D7KtHWmjzhqkTnVedr1NG3',
    'BAsAbV6kzhczKaVUzbbDt11ir6QYDkHTJ7bgUxVdpSoJ',
    '76yS3U99Ejb6swgBwPxhkrQcH2jbMTN4KZjCR27S64mt',
    'E1bmuXsDYbAWXyF7jD1w3aAagJZWmfFnp44hz46sj1eY',
    'KvS8AdzYd24ufE9RoXC5hSG1TBMYgeQwNAR9AjYnHMS',
    'DJfGpWbxbWyYfjgDbDvmBXrUDC2JMV5xyKJPErj1hNv4',
    'HH4n6hDkak1wobC8MfRfFPiaLvBEn24cDmUtKejNX5Ey',
    'DkaiMZe1V829xUEKB8LYwm3RBNqZbU8ARF1ddURZnrZg',
    'GxdMZoXVdWeXcZJsNpQbBbURzMKLhWmqHXXNthyFnukp',
    'Anksv5GGAdD4XsbuSDJYZEK8unRPAY14uyqtcXmssNAV',
    '4d52aY94ctK8wqVejNNfXuY6zbNLHWT1VdKmXuV2XscD',
    'HTsZs7zrSMPxuq9oKyW1m5NZcQt22rbQrXscE7j4fxJK',
    'giLkCXycxMP9u2Z6jBQ7Hr4E7ui7WS49gDka1Yvqymn',
    'CgQXt5hVJMF5sd2XijVknbhsWzsbByyYLBeKyj1VTEpw',
    '55X5BunVafshC8AjzpRUCKMy9k4Z8ZGjfbsjjtXQzxrL',
    'HtKPdEwHfsu2pEQ6TADKeKpiENvfEkrnSmFDcxcSCn6m',
    'FjsPx5cRBxLUxpi86SwaCsi2j2dswUVth1Y3uLzEmbG8',
    'E5YT9wgyPUtFrfmM6jTjUmpZxWCN4HWBf7nZi5p2qJbK',
    '36uhrwu8bRgzVQGFJs9UbebppyHRrWwx6m49BdsgApvD',
    'FwuCDc4BUpmsTNCWbvvZA7gYZr5ow1N4X4d6RdyAP8UT',
    '6B1zVzMqZvjEWT5HyJg83WTwQLF7j8wdbDGkCeRs5FRv',
    '3TEpufUCvs2bGbnfwe6xWtA7UxPDo8D3iVj6Be5rgeVF',
    'CJYLwZQXkSaawsdfYtSWs2LAvR2dp91VRsm7UcrkZmb8',
    '4KF3XCeSLEHC1AZNjXy5ap47oKLr6aecGuLmmo75859N',
    '4CRJ95N49P1Kzp3TizRA54GgRkLPzyQVb7j3MkWtVTv7'
    )
    AND (d.addr IS NULL OR d.addr = '')
)
SELECT
  t.source_owner           AS host,
  toDate(t.block_time)     AS day,
  CASE
    WHEN t.destination_owner = 'Epz7DFBNZrve9c2pU6NovEsa6n7mU62qy2GRgXVuNqA3' THEN 'cex'
    WHEN t.destination_owner IN (
      'ARu4n5mFdZogZAravu7CcizaojWnS6oqka37gdLT5SZn',  -- OKX DEX router
      '3GkFzURGWNWyErnjQvnkZpgcLnNocjnRwvMYXiVDiVQk',  -- Raydium NOS-USDC
      'JS4VAUXFkMvtbxWxUVNG48SRK6QCkqThzED83QXvZsQ',   -- Raydium WSOL-NOS
      '3fCMZfWg48aUNYtdPm9KG4kmwseenr446fLAnafd2Uvj',  -- Orca SOL-NOS
      'D5YqVMoSxnqeZAKAUUE1Dm3bmjtdxQ5DCF356ozqN9cM',  -- Titan Exchange
      '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1'   -- Raydium Authority V4
    ) THEN 'dex'
    WHEN t.destination_owner IN (
      '9uVHh78UKrZxAvK9ytm6BkMAFarpB3aqnbYdS6VK4pyq',
      '7YGRTc8mZ2sfB86rvafyoMYo5KZK2LtAch2LTXD3bTM7',
      'EkTvSTm9TM1u5L4FHfvwkue2RUuGpGXTGtBZGK7kLdR5'
    ) THEN 'consolidated_emptied'
    WHEN t.destination_owner IN (
      'JC6fRXboak6rsoMb5WPu5HzDSrTcVWB4N7pWdKVZd3PS',
      'FHNGA3iZ8Suy5DxbQvYnp4RGC5bbhSRyPYc3o5e2dnvq'
    ) THEN 'consolidated_kept'
    ELSE 'other'
  END                      AS category,
  SUM(t.amount) / 1e6      AS sent
FROM solana.transfers AS t
INNER JOIN hosts AS h ON t.source_owner = h.host
WHERE t.mint = 'nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7'
GROUP BY host, day, category
ORDER BY host, day
