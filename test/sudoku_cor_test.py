# -*- coding: utf-8 -*-
"""Test statistical independence of components of generated sample."""

from __future__ import division, print_function, absolute_import

import numpy as np

import sudoku_lhs.sudoku as sudoku
import sudoku_lhs.lhs as lhs  # classical LHS, for comparison

# emulate MATLAB corr(X) - pairwise linear correlation coefficient of columns of x
#
# x : rank-2 np.array
#     data, size (nrow, ncol)
#
# out : rank-2 np.array
#     correlation coefficient array, size (ncol, ncol)
#
def corr(x):
    ncol = x.shape[1]
    out  = np.empty( (ncol,ncol), dtype=np.float64, order="C" )
    for j in range(ncol):
        for k in range(ncol):
            out[j,k] = np.corrcoef( x[:,j], x[:,k] )[0,1]  # corrcoeff[0,1] = correlation between columns j and k  ( [0,0] is j,j  and [1,1] is k,k,  which are always 1 )
    return out

def get_max_corr(R):
    n = R.shape[0] # == R.shape[1]
    tmp = R - np.eye(n)  # remove the ones on the diagonal (they do not contain any useful information)
    return np.max(np.abs(tmp))


def test():
    ndim  = 4  # Number of dimensions.
    nsam  = 10 # Subdivisions ("k") for sudoku LHS. Needs to be about 10 for meaningful results.

    nreps = 10 # This many sets of nruns runs will be performed.
    nruns = 10 # This many runs will be performed for each set. Needs to be large (e.g. 1000) for meaningful results.

    nlhs = nsam**ndim
    print( "Monte Carlo vs. LHS with %d samples vs. sudoku LHS with %d sudoku boxes in %d dimensions." % (nlhs, nsam, ndim) )
    print( "Performing %d sets of %d runs." % (nreps, nruns) )

    means_MC        = np.zeros( (nreps,), dtype=np.float64 )
    means_LHS       = np.zeros( (nreps,), dtype=np.float64 )
    means_SudokuLHS = np.zeros( (nreps,), dtype=np.float64 )

    xxlhs = np.arange(nlhs)
    for j in range(nreps):
        print( 'Set %d of %d...' % (j+1, nreps) )

        unique_MC      = np.zeros( (nruns,), dtype=np.float64 )
        cors_MC        = np.zeros( (nruns,), dtype=np.float64 )	
        cors_LHS       = np.zeros( (nruns,), dtype=np.float64 )
        cors_SudokuLHS = np.zeros( (nruns,), dtype=np.float64 )

        for k in range(nruns):
            # comparison: plain (pseudo-) Monte Carlo
            xxmc = []
            for l in range(ndim):
                xxmc.append( np.floor(nlhs*np.random.random(nlhs)) )  # nlhs random integers in range(nlhs)

            a = np.array( xxmc, dtype=np.float64 ).T
            c = corr(a)
            cors_MC[k] = get_max_corr(c)
            # LHS always produces unique values, MC is not guaranteed to.
            unique_MC[k] = 100.0 * len(np.unique(a.reshape(-1))) / nlhs

            # traditional LHS
            #
            a = lhs.sample(ndim, nlhs)
            c = corr(a)
            cors_LHS[k] = get_max_corr(c)

            # sudoku LHS
            a,m = sudoku.sample(ndim,nsam,1)
            c = corr(a)
            cors_SudokuLHS[k] = get_max_corr(c)

        uMC        = np.mean(unique_MC)
        mMC        = np.mean(cors_MC)
        mLHS       = np.mean(cors_LHS)
        mSudokuLHS = np.mean(cors_SudokuLHS)

        vMC        = np.var(cors_MC)
        vLHS       = np.var(cors_LHS)
        vSudokuLHS = np.var(cors_SudokuLHS)

        print( 'Mean correlation (MC): %0.6g, variance %0.6g, mean uniq. bins %0.3g%%' % (mMC, vMC, uMC) )
        print( 'Mean correlation (LHS): %0.6g, variance %0.6g' % (mLHS, vLHS) )
        print( 'Mean correlation (Sudoku LHS): %0.6g, variance %0.6g' % (mSudokuLHS, vSudokuLHS) )
        print( 'Improvement (over MC): %0.6gx' % (abs(mMC/mSudokuLHS)) )
        print( 'Improvement (over LHS): %0.6gx' % (abs(mLHS/mSudokuLHS)) )

        means_MC[j]        = mMC
        means_LHS[j]       = mLHS
        means_SudokuLHS[j] = mSudokuLHS

    print("All done.")

    mMC        = np.mean(means_MC)
    mLHS       = np.mean(means_LHS)
    mSudokuLHS = np.mean(means_SudokuLHS)

    vMC        = np.var(means_MC)
    vLHS       = np.var(means_LHS)
    vSudokuLHS = np.var(means_SudokuLHS)

    print( "Mean correlation over all runs (MC): %0.6g (var. over sets %0.6g)" % (mMC, vMC) )
    print( 'Mean correlation over all runs (LHS): %0.6g (var. over sets %0.6g)' % (mLHS, vLHS) )
    print( 'Mean correlation over all runs (Sudoku LHS): %0.6g (var. over sets %0.6g)' % (mSudokuLHS, vSudokuLHS) )
    print( 'Improvement (over MC): %0.6gx' % (abs(mMC/mSudokuLHS)) )
    print( 'Improvement (over LHS): %0.6gx' % (abs(mLHS/mSudokuLHS)) )


if __name__ == '__main__':
    test()

