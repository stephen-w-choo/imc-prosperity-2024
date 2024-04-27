This is the code I wrote for IMC Prosperity 2024. It's a 5 round algorithmic challenge. 

I have no experience in trading whatsoever, especially algorithmic trading, but this was still a very fun exercise in manipulating data and looking for patterns.

The code is not pretty, so please excuse me - I found the time constraints in this contest to be extremely tight, mostly due to the fact that:
1. I was a one person team, and couldn't really share the work with anyone else
2. I was working on this while juggling full-time work

Still - I'm happy with the result overall.


## Retrospective
### Round 1
Two resources, with a fairly straightforward pattern.

I created a simple function that would both market-take and market-make based on fluctuations around a perceived 'ideal' price - this function would actually become the backbone of my scripts for the rest of the competition.

Modelling the ideal price for Amethysts was easy enough - it was a stable price. Starfruit could be modelled with a simple time-delayed linear regression.

For manual trading - I suspect I misinterpreted the instructions - I expected 'linear probability' to be a straight line - if this was the case, 933 and 966 would have been optimal - however, it looks like 950 and 975 were the actual optimal values.

### Round 2
A single new resource, Orchids, trading over two markets. This looked like a case for arbitrage, but I couldn't see the same opportunities that everyone else did. I still haven't cracked the code for the signal that others were using - as a result, my algorithm underperformed quite a bit compared to everyone else.

Manual trading was a straightforward graph theory/combinatrics problem, which was a nice breather (and I'm confident my solution was optimal)

### Round 3
A composite resource and three component resources.
There was a fairly clear correlation between the price of the gift basket and it's components (with a fairly consistent premium on the gift basket), but I couldn't get an accurate model with this one.
I eventually ended up with a time-delayed linear regression again, using the price of the components to predict the composite, but the performance was still subpar. There are definitely more sophisticated strategies, but I was hitting the limit of my rather limited data science skills at this point.

Manual trading was interesting this round, since it was quite a bit more luck dependent - you had to make a bet that other people wouldn't choose the same squares you did. I made an educated guess and came out reasonably well, but I'm not sure how much of that is skill on my part.

#### Round 4
Oh boy - this one was trading options, something which looks incredibly risky in real life and which I would never try with my own money.

I created a slightly convoluted method - which ended up erroring the lambda, and the algorithm didn't run at all.

This may have been a blessing in disguise - as it turned out, a large number of teams lost their shirts while attempting to trade the highly volatile option

Manual trading was a remix of the first round - straightforward, and I was able to get it close to optimal.
