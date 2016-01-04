logsumexp <- function(x) {
  ## Add numbers represented in log space without underflowing.
  ##
  ## Arguments
  ## ---------
  ## x : A numeric vector
  ##
  ## returns : the log of the sum of the elements in x (a scalar).
  ##
  m <- max(x)
  m + log(sum(exp(x - m)))
}
