This is the code I wrote for IMC Prosperity 2024. It's a 5 round algorithmic challenge. 

I participated as a solo competitor, under the team name 'FeathersIsland'. Final result was 489th overall out of 9140 teams worldwide (and 36th in Australia).

I have no experience in trading whatsoever, especially algorithmic trading, but this was still a very fun exercise in manipulating data and looking for patterns.

The code is not pretty, so please excuse me - I found the time constraints in this contest to be extremely tight, mostly due to the fact that:
1. I was a one person team, and couldn't really share the work with anyone else
2. I was working on this while juggling full-time work

Still - I'm happy with the result overall for my first contest.


## Retrospective
### Round 1
Two resources, with a fairly straightforward pattern.

I created a simple function that would both market-take and market-make based on fluctuations around a perceived 'ideal' price - this function would actually become the backbone of my scripts for the rest of the competition.

Modelling the ideal price for Amethysts was easy enough - it was a stable price. Starfruit could be modelled with a simple time-delayed linear regression.

For manual trading - I suspect I misinterpreted the instructions - I expected 'linear probability' to be a straight line - if this was the case, 933 and 966 would have been optimal - however, it looks like 950 and 975 were the actual optimal values.

### Round 2
A single new resource, Orchids, trading over two markets. This looked like a case for arbitrage, but I couldn't see the same opportunities that everyone else did. I still haven't cracked the code for the signal that others were using - as a result, my algorithm underperformed quite a bit compared to everyone else.

Reading through the winning team's implementation, it looks like the key was to monitor the price, and try and short the existing market whenever the conversion price dipped below the threshold, then convert back the following round. This was, broadly speaking, how I attempted it, except I attempted to go long on the market as well, which was likely the mistake.

Manual trading was a straightforward graph theory/combinatrics problem, which was a nice breather (and I'm confident my solution was optimal)

### Round 3
A composite resource and three component resources.
There was a fairly clear correlation between the price of the gift basket and it's components (with a fairly consistent premium on the gift basket), but I couldn't get an accurate model with this one.
The key was obviously to buy/sell around the gift basket price, using the components as a marker, but I couldn't get an effective/accurate way of estimating what the premium of the gift basket 'should' be.
I eventually ended up with a time-delayed linear regression again, using the price of the components to predict the composite, but the performance was still subpar. There are definitely more sophisticated strategies, but I was hitting the limit of my rather limited data science skills at this point.

Manual trading was interesting this round, since it was quite a bit more luck dependent - you had to make a bet that other people wouldn't choose the same squares you did. I made an educated guess and came out reasonably well, but I'm not sure how much of that is skill on my part.

### Round 4
Oh boy - this one was trading options, something which looks incredibly risky in real life and which I would never try with my own money.

I created a slightly convoluted method with a moving average to try and trade coconuts. This worked in the rests, but it ended up erroring the lambda on the actual run, and the algorithm didn't run at all.

This may have been a blessing in disguise - as it turned out, a large number of teams lost their shirts while attempting to trade the highly volatile option

It looks like the ideal model here would have been based on something called Black-Scholes to calculate the price of the option, although this was beyond my skills to implement, and I was too time-constrained to learn it.

Manual trading was a remix of the first round - straightforward, and I was able to get it close to optimal.

### Round 5
The final round - this time we had the trading data de-anonymised, will full knowledge of the trader behind each trade.

I made a few scripts to graph each trader's results and buys/sells. I was only able to find one credible marker that I was confident - that Rhianna would sell ROSES at peak price, and buy at the floor price. I followed her trades for roses, and this marker did quite well, but I unfortunately could not compete with other teams with multiple markers.

In hindsight, the flaw in my analysis was just considering the buyer/seller - and not separating out those trades into the recipients of each trade, which would probably have yielded more markers.

Manual trading was... interesting. This round definitely felt more subjective than the others. I ended up getting 75k - roughly middle of the pack, and about half of the optimal 150k
